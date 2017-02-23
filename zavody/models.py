# coding: utf-8
from datetime import date

from django.db import models
from django.db.models import Count
from django.utils.text import slugify

from zavodnici.models import Zavodnik

def _string_to_ordering_kwargs(razeni='vysledny_cas--startovni_cas--cislo'):
    ordering_kwargs = {
        'prvni': ['nedokoncil'],
        'count': ['-vysledny_cas'],
        'razeni': ['vysledny_cas', 'startovni_cas', 'cislo']
    }
    if razeni:
        ordering_kwargs['razeni'] = razeni.split('--')
    return ordering_kwargs


class Sport(models.Model):
    nazev = models.CharField(u'Název', max_length=50, unique=True)
    slug = models.SlugField(editable=False)
    info = models.TextField(u'Info', null=True, blank=True)

    class Meta:
        verbose_name = u'Sport'
        verbose_name_plural = u'Sporty'

    def __unicode__(self):
        return self.nazev

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nazev)
        return super(Sport, self).save(*args, **kwargs)


class Zavod(models.Model):
    nazev = models.CharField(u'Název', max_length=50, unique=True)
    slug = models.SlugField(editable=False, unique=True)
    sport = models.ForeignKey(
        'Sport',
        verbose_name=u'sport',
        related_name='zavody')
    korekce_sezony = models.BooleanField(
        u'Korekce sezóny',
        help_text=u'zatrhni u podzimních lyžařských běhů pro použití kategorií zimní sezóny',
        default=False)
    misto = models.CharField(u'Místo', max_length=120, null=True, blank=True)
    info = models.TextField(u'Info', null=True, blank=True)

    class Meta:
        verbose_name = u'Závod'
        verbose_name_plural = u'Závody'

    def __unicode__(self):
        return self.nazev

    @models.permalink
    def get_absolute_url(self):
        return ('zavody:zavod_detail', (self.id,))

    @models.permalink
    def get_delete_url(self):
        return ('zavody:zavod_smazani', (self.id,))

    def save(self, *args, **kwargs):
        self.slug = slugify(self.nazev)
        return super(Zavod, self).save(*args, **kwargs)

    def posledni_rocnik(self):
        return self.rocniky.first()


class Rocnik(models.Model):
    zavod = models.ForeignKey(Zavod,
                              verbose_name=u'závod',
                              related_name='rocniky')
    nazev = models.CharField(
        u'Název', max_length=50, null=True, blank=True,
        help_text=u'pokud není název vyplněn, pak se dědí z rodičovského závodu')
    datum = models.DateField(u'Datum pořádání')
    cas = models.TimeField(u'Čas', null=True, blank=True)
    misto = models.CharField(
        u'Místo konání', max_length=120, null=True, blank=True,
        help_text=u'pokud není místo vyplněno, pak se dědí z rodičovského závodu')
    info = models.TextField(u'Info', null=True, blank=True)

    class Meta:
        verbose_name = u'Ročník závodu'
        verbose_name_plural = u'Ročníky zavodů'
        ordering = ('-datum',)
        unique_together = ('zavod', 'datum')

    def __unicode__(self):
        nazev = self.nazev or self.zavod.nazev
        return u'{0} {1}'.format(
            nazev, self.datum.year)

    @models.permalink
    def get_absolute_url(self):
        return ('zavody:rocnik_detail', (self.id,))

    @models.permalink
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
            zpravy.append(u'pro "{0}" nenalezena vhodná kategorie'.format(nezarazen.clovek))

        Zavodnik.objects.filter(id__in=[z.id for z in nezarazeni]).update(kategorie_temp=None)
        return zpravy

    def kategorie_list(self, razeni=None):
        kategorie_list = []
        for kategorie in self.kategorie.all():
            kategorie_list.append([kategorie, kategorie.serazeni_zavodnici(razeni)])
        return kategorie_list

    def nezarazeni(self, razeni=''):
        razeni_list = razeni.split('--')
        return self.zavodnici.filter(kategorie_temp=None).order_by(*razeni_list)


def kategorie_test_cloveka(kategorie, zavodnik, narozeni):
    """testuje zavodnika jako cloveka na prvky kategorie
    pouzito u: zavody.Kategorie, pohary.KategirePoharu"""
    if zavodnik.clovek:
        vhodny = True
        if zavodnik.clovek.narozen not in range(narozeni[0], narozeni[1] + 1):
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
        ('m', u'muži'),
        ('z', u'ženy'),
    )
    nazev = models.CharField(u'Název', max_length=50)
    znacka = models.CharField(
        u'Značka', max_length=10,
        null=True, blank=True,
        help_text=u'značka kategorie se použije při\
        porovnávání s vnucenými kategoriemi závodníků <b>u kategorií pohárů</b>')
    pohlavi = models.CharField(
        u'Pohlaví', max_length=1, choices=POHLAVI,
        null=True, blank=True)
    vek_od = models.SmallIntegerField(
        u'Věk od', null=True, blank=True,
        help_text=u'věk závodníka včetně')
    vek_do = models.SmallIntegerField(
        u'Věk do', null=True, blank=True,
        help_text=u'věk závodníka včetně')
    atributy = models.ManyToManyField(
        'lide.Atribut', verbose_name=u'Požadované atributy člověka', blank=True
        # null=True,
        )
    delka_trate = models.CharField(
        u'Délka tratě', null=True, blank=True, max_length=20)
    rocnik = models.ForeignKey(
        Rocnik, verbose_name=u'ročník',
        related_name='kategorie')
    poradi = models.SmallIntegerField(
        u'Pořadí', null=True, blank=True)
    spusteni_stopek = models.TimeField(
        u'Čas spuštění stopek kategorie',
        null=True, blank=True,
        help_text=u'středoevropský čas, kdy byli pro kategorii spuštěny stopky')

    class Meta:
        verbose_name = u'Kategorie'
        verbose_name_plural = u'Kategorie'
        unique_together = (('rocnik', 'nazev'),)
        ordering = ('poradi', 'id')

    def __unicode__(self):
        popis = u'{0} - {1}'.format(
            self.nazev,
            self.get_pohlavi_display() or 'unisex')
        if self.znacka:
            popis = self.znacka + ' - ' + popis
        if self.vek_od or self.vek_do:
            popis += u' / {0}-{1}'.format(
                self.vek_od or '?',
                self.vek_do or '?')
        return popis

    @models.permalink
    def get_absolute_url(self):
        return ('zavody:kategorie_detail', (self.id,))

    def rozsah_narozeni(self):
        rok = self.rocnik.datum.year
        # korekce pro sezonu zari-duben
        if self.rocnik.zavod.korekce_sezony:
            rok += 1
        return (
            rok - (self.vek_do or 200),
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
                        zprava = u'"{0}" je již v kategorii "{1}" přítomen! Proto nezařazen.'
                    else:
                        zprava = u'"{0}" je již v kategorii "{1}" přítomna! Proto nezařazena.'
                    zpravy.append(zprava.format(zavodnik.clovek, self.nazev))
                else:
                    zarazeni_lide.add(zavodnik.clovek)
                    zarazeni.append(zavodnik)
            else:
                nezarazeni.append(zavodnik)

        # ulozeni kategorie do Zavodnik.kategorie_temp
        Zavodnik.objects.filter(id__in=[i.id for i in zarazeni]).update(kategorie_temp=self)
        return (nezarazeni, duplikati, zpravy)

    def serazeni_zavodnici(self, razeni):
        "vrati serazene zavodniky kategorie a doplni do nich casove ztraty na prvniho"
        # pomoci annotate Count, se radi prazdna pole na konec (null_value = 1 / 0)
        annotate_kwargs = {}
        ordering_kwargs = _string_to_ordering_kwargs(razeni)
        ordering_list = ordering_kwargs['prvni']
        for i in ordering_kwargs['count']:
            actual = i + '_value'
            annotate_kwargs[actual.strip('-')] = Count(i.strip('-'))
            ordering_list.append(actual)
        ordering_list += ordering_kwargs['razeni']

        zavodnici = self.zavodnici_temp.all()\
                .annotate(**annotate_kwargs)\
                .order_by(*ordering_list)

        # vypocet casove ztraty na prvniho
        if zavodnici:
            nejlepsi_cas = zavodnici[0].vysledny_cas
            if nejlepsi_cas:
                for i, zavodnik in enumerate(zavodnici[1:], 1):
                    cas = zavodnik.vysledny_cas
                    if cas:
                        zavodnici[i].casova_ztrata = cas - nejlepsi_cas

        return zavodnici
