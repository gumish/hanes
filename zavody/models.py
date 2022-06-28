from datetime import date

from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils.text import slugify

from zavodnici.models import Zavodnik


def _string_to_ordering_kwargs(razeni='', ignoruj_nedokoncil=False):
    """ Pripravy slovnik pro vyzuziti v query
    Args:
        razeni (str): string pro prevod ordering_kwargs['razeni']
        ignoruj_nedokoncil (bool): zruseni zarazovani DNS na konec
    Returns:
        ordering_kwargs (dict): slovnik pouzity dale u query
            'prvni': prvni polozky v budoucim 'order_by'
            'count': dalsi polozky 'order_by', ktere pokud budou prazdne, tak se budou radit na konec
            'razeni': posledni polozky, ktere se pouze pripoji na konec
    """
    # TODO: vyuzit from django.db.models import F | .order_by(F('price').desc(nulls_last=True))
    if not ignoruj_nedokoncil:  # normalni razeni - neignoruje nedokoncil
        ordering_kwargs = {
            'prvni': ['nedokoncil'],  # None jde na zacatek
            'count': ['-vysledny_cas', 'startovni_cas'],
            'razeni': ['vysledny_cas', 'startovni_cas', 'cislo']
        }
    else:  # ignoruje diskvalifikace, radi jen podle casu
        ordering_kwargs = {
            'prvni': [],
            'count': [],
            'razeni': ['vysledny_cas', 'startovni_cas', 'cislo']
        }
    if razeni:
        ordering_kwargs['razeni'] = razeni.split('--')
    return ordering_kwargs


class Sport(models.Model):
    nazev = models.CharField('Název', max_length=50, unique=True)
    slug = models.SlugField(editable=False)
    info = models.TextField('Info', null=True, blank=True)

    class Meta:
        verbose_name = 'Sport'
        verbose_name_plural = 'Sporty'

    def __str__(self):
        return self.nazev

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nazev)
        return super(Sport, self).save(*args, **kwargs)


class Zavod(models.Model):
    nazev = models.CharField('Název', max_length=50, unique=True)
    slug = models.SlugField(editable=False, unique=True)
    sport = models.ForeignKey(
        'Sport',
        verbose_name='sport', related_name='zavody',
        on_delete=models.CASCADE)
    korekce_sezony = models.BooleanField(
        'Korekce sezóny',
        help_text='zatrhni u podzimních lyžařských běhů pro použití kategorií zimní sezóny',
        default=False)
    misto = models.CharField('Místo', max_length=120, null=True, blank=True)
    info = models.TextField('Info', null=True, blank=True)

    class Meta:
        verbose_name = 'Závod'
        verbose_name_plural = 'Závody'
        ordering = ('-rocniky__datum', 'sport', 'nazev')  #zavody serazeny od nejaktualnejsiho

    def __str__(self):
        return self.nazev

    def get_absolute_url(self):
        return reverse('zavody:zavod_detail', args=(self.id,))

    def get_delete_url(self):
        return ('zavody:zavod_smazani', (self.id,))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nazev)
        return super(Zavod, self).save(*args, **kwargs)

    def posledni_rocnik(self):
        return self.rocniky.first()


class Rocnik(models.Model):
    zavod = models.ForeignKey(
        Zavod,
        verbose_name='závod', related_name='rocniky',
        on_delete=models.CASCADE)
    nazev = models.CharField(
        'Název', max_length=50, null=True, blank=True,
        help_text='pokud není název vyplněn, pak se dědí z rodičovského závodu')
    datum = models.DateField('Datum pořádání')
    cas = models.TimeField('Čas', null=True, blank=True)
    misto = models.CharField(
        'Místo konání', max_length=120, null=True, blank=True,
        help_text='pokud není místo vyplněno, pak se dědí z rodičovského závodu')
    info = models.TextField('Info', null=True, blank=True)

    class Meta:
        verbose_name = 'Ročník závodu'
        verbose_name_plural = 'Ročníky zavodů'
        ordering = ('-datum',)
        unique_together = ('zavod', 'datum')

    def __str__(self):
        nazev = self.nazev or self.zavod.nazev
        return '{0} {1}'.format(
            nazev, self.datum.year)

    def get_absolute_url(self):
        return reverse('zavody:rocnik_detail', args=(self.id,))

    def get_delete_url(self):
        return ('zavody:rocnik_smazani', (self.id,))

    def get_misto(self):
        return self.misto or self.zavod.misto

    def rozkategorizovat_zavodniky(self):
        def _kategorie_sorter(kategorie):
            return kategorie.atributy.all().count()

        kategorie = list(self.kategorie.all())
        # srovnani kategorii dle dulezitosti pri rozdleovani zavodniku
        kategorie.sort(key=_kategorie_sorter)
        kategorie.reverse()
        nezarazeni = list(self.zavodnici.all())
        duplikati = set()
        zpravy = []

        for kateg in kategorie:
            # kategorie si sama profiltruje jake bude obsahovat zavodniky
            nezarazeni, duplikati_kategorie, zpravy_kategorie = kateg.zavodnici_filtr(nezarazeni)
            duplikati.update(duplikati_kategorie)
            zpravy += zpravy_kategorie

        for nezarazen in set(nezarazeni).difference(duplikati):
            zpravy.append('pro "{0}" nenalezena vhodná kategorie'.format(nezarazen.clovek))

        Zavodnik.objects.filter(id__in=[z.id for z in nezarazeni]).update(kategorie_temp=None)
        return zpravy

    def kategorie_list(self, razeni=None, ignoruj_nedokoncil=False):
        """ Vrati list kategorii [(kategorie, zavodidnici), ...] """
        kategorie_list = []
        for kategorie in self.kategorie.all():
            kategorie_list.append(
                (kategorie, kategorie.serazeni_zavodnici(razeni, ignoruj_nedokoncil))
            )
        return kategorie_list

    def nezarazeni(self, razeni=''):
        razeni_list = razeni.split('--')
        return self.zavodnici.filter(kategorie_temp=None).order_by(*razeni_list)


def kategorie_test_cloveka(kategorie, zavodnik, narozeni):
    """testuje zavodnika jako cloveka na prvky kategorie
    pouzito u: zavody.Kategorie, pohary.KategirePoharu"""
    if zavodnik.clovek:
        vhodny = True
        if zavodnik.clovek.narozen not in list(range(narozeni[0], narozeni[1] + 1)):
            vhodny = False
        if kategorie.pohlavi:
            if zavodnik.clovek.pohlavi != kategorie.pohlavi:
                vhodny = False
        if kategorie.atributy:
            atributy_cloveka = zavodnik.clovek.atributy.all()
            for attr in kategorie.atributy.all():
                if attr not in atributy_cloveka:
                    vhodny = False
        return vhodny
    else:
        return False


class Kategorie(models.Model):
    POHLAVI = (
        ('m', 'muži'),
        ('z', 'ženy'),
    )
    nazev = models.CharField('Název', max_length=50)
    znacka = models.CharField(
        'Značka', max_length=10,
        null=True, blank=True,
        help_text='značka kategorie se použije při\
        porovnávání s vnucenými kategoriemi závodníků <b>u kategorií pohárů</b>')
    pohlavi = models.CharField(
        'Pohlaví', max_length=1, choices=POHLAVI,
        null=True, blank=True)
    vek_od = models.SmallIntegerField(
        'Věk od', null=True, blank=True,
        help_text='věk závodníka včetně, pokud není vyplněn bere se jako 0')
    vek_do = models.SmallIntegerField(
        'Věk do', null=True, blank=True,
        help_text='věk závodníka včetně, pokud není vyplněn bere se jako neomezený! (nepsat zbytečně 100 atd.)')
    atributy = models.ManyToManyField(
        'lide.Atribut', verbose_name='Požadované atributy člověka', blank=True
        # null=True,
        )
    delka_trate = models.CharField(
        'Délka tratě', null=True, blank=True, max_length=20)
    rocnik = models.ForeignKey(
        Rocnik,
        verbose_name='ročník', related_name='kategorie',
        on_delete=models.CASCADE)
    poradi = models.SmallIntegerField(
        'Pořadí', null=True, blank=True)
    spusteni_stopek = models.TimeField(
        'Čas spuštění stopek kategorie',
        null=True, blank=True,
        help_text='středoevropský čas, kdy byli pro kategorii spuštěny stopky')
    startovne = models.SmallIntegerField(
        'Startovné', null=True, blank=True)


    class Meta:
        verbose_name = 'Kategorie'
        verbose_name_plural = 'Kategorie'
        unique_together = (('rocnik', 'nazev'),)
        ordering = ('poradi', 'id')

    def __str__(self):
        popis = '{0} - {1}'.format(
            self.nazev,
            self.get_pohlavi_display() or 'unisex')
        if self.znacka:
            popis = self.znacka + ' - ' + popis
        if self.vek_od or self.vek_do:
            popis += ' / {0}-{1}'.format(
                self.vek_od or '?',
                self.vek_do or '?')
        return popis

    def get_absolute_url(self):
        return reverse('zavody:kategorie_detail', args=(self.id,))

    def rozsah_narozeni(self):
        """ vrati tuple roku narozeni
            pokud neni vek vyplnen vrati 0 nebo aktualni rok
        """
        rok = self.rocnik.datum.year
        # korekce pro sezonu zari-duben
        if self.rocnik.zavod.korekce_sezony:
            rok += 1
        if self.vek_do:
            rok_od = rok - self.vek_do
        else:
            rok_od = 0
        return (
            rok_od,
            min((rok - (self.vek_od or 0), date.today().year))
        )

    def zavodnici_filtr(self, zavodnici=None):
        '''ze vstupnich `nezarazeni` odfiltruje svoje vhodne zavodniky
        a vrati dvojici `zarazeni / nezarazeni`'''
        zarazeni = []
        zarazeni_lide = set()
        nezarazeni = []
        duplikati = []
        zpravy = []
        for zavodnik in zavodnici:
            vhodny = False
            # testovat pouze neprirazene zavodniky
            if not zavodnik.kategorie:
                vhodny = kategorie_test_cloveka(self, zavodnik, self.rozsah_narozeni())

            if vhodny or zavodnik.kategorie == self:
                if zavodnik.clovek in zarazeni_lide:
                    duplikati.append(zavodnik)
                    nezarazeni.append(zavodnik)
                    if zavodnik.clovek.pohlavi == 'm':
                        zprava = '"{0}" je již v kategorii "{1}" přítomen! Proto nezařazen.'
                    else:
                        zprava = '"{0}" je již v kategorii "{1}" přítomna! Proto nezařazena.'
                    zpravy.append(zprava.format(zavodnik.clovek, self.nazev))
                else:
                    zarazeni_lide.add(zavodnik.clovek)
                    zarazeni.append(zavodnik)
            else:
                nezarazeni.append(zavodnik)

        # ulozeni kategorie do Zavodnik.kategorie_temp
        Zavodnik.objects.filter(id__in=[i.id for i in zarazeni]).update(kategorie_temp=self)
        return (nezarazeni, duplikati, zpravy)

    def serazeni_zavodnici(self, razeni, ignoruj_nedokoncil=False):
        """ Seradi zavodniky kategorie
        Args:
            razeni (str), ignoruj_nedokoncil (bool): parametry predane fci _string_to_ordering_kwargs
        Returns:
            zavodnici (list): serazeni zavodnici dle 'ordering_kwargs' s dpolnenymi ztratami na prvnihio
        """
        annotate_kwargs = {}
        ordering_kwargs = _string_to_ordering_kwargs(razeni, ignoruj_nedokoncil)
        vysledne_razeni = ordering_kwargs['prvni']
        # print(ordering_kwargs['count'])
        for i in ordering_kwargs['count']:
            actual = i + '_value'
            annotate_kwargs[actual.strip('-')] = Count(i.strip('-'))  # pomoci annotate Count, se radi prazdna pole na konec (null_value = 1 / 0)
            vysledne_razeni.append(actual)
        vysledne_razeni += ordering_kwargs['razeni']

        zavodnici = self.zavodnici_temp.all()\
                .annotate(**annotate_kwargs)\
                .order_by(*vysledne_razeni)

        # vypocet casove ztraty na prvniho
        if zavodnici:
            nejlepsi_cas = zavodnici[0].vysledny_cas
            if nejlepsi_cas:
                for i, zavodnik in enumerate(zavodnici[1:], 1):
                    # zavodnik ktery nedokoncil se nepocita ztrata
                    if not zavodnik.nedokoncil and zavodnik.vysledny_cas:
                        zavodnici[i].casova_ztrata = zavodnik.vysledny_cas - nejlepsi_cas

        return zavodnici
