# coding: utf-8
from operator import attrgetter
from datetime import date

from django.db import models
from django.utils.text import slugify

# from zavody.models import Rocnik
from zavodnici.models import Zavodnik
from zavody.models import kategorie_test_cloveka


class Pohar(models.Model):
    zavodnici_s_kategorii = []
    nazev = models.CharField(u'Název', max_length=50)
    datum = models.DateField(u'Datum pořádání')
    slug = models.SlugField(editable=False, unique=True)
    info = models.TextField(u'Info', null=True, blank=True)
    zavodu = models.SmallIntegerField(
        u'Počet nejlepších výsledků',
        help_text=u'počet nejlepších závodů jež budou započítany,<br>\
        při prázdné kolonce budou použity všechny závody',
        blank=True, null=True)
    bod_hodnoceni = models.ForeignKey(
        'BodoveHodnoceni', verbose_name=u'Bodové hodnocení',
        help_text=u'bodová tabulka pro pohár,<br>\
        bude použita v případě nespecifikované tabulky u kategorie,<br>\
        v případě prázdného kolonky se boduje postupně odzadu',
        related_name='pohary', on_delete=models.CASCADE,
        blank=True, null=True)
    rocniky = models.ManyToManyField(
        'zavody.Rocnik', verbose_name=u'Ročníky', related_name='pohary')

    class Meta:
        verbose_name = u'Pohár'
        verbose_name_plural = u'Poháry'
        ordering = ('-datum',)
        unique_together = ('nazev', 'datum')

    def __unicode__(self):
        return self.nazev

    @models.permalink
    def get_absolute_url(self):
        return ('pohary:pohar_detail', (self.slug,))

    @models.permalink
    def get_delete_url(self):
        return ('pohary:pohar_smazani', (self.slug,))

    def save(self, *args, **kwargs):
        self.slug = '{0}_{1}'.format(slugify(self.nazev), self.datum.year)
        return super(Pohar, self).save(*args, **kwargs)

    def rocniky_chronologicky(self):
        return self.rocniky.all().order_by('datum')

    def prvni_rocnik(self):
        return self.rocniky_chronologicky().first()

    def zavodnici_vsichni(self):
        zavodnici = Zavodnik.objects.filter(
            rocnik__in=self.rocniky.all(), vysledny_cas__isnull=False, nedokoncil=None) \
            .order_by('rocnik__datum', 'vysledny_cas')
        return zavodnici

    def zavodnici_bez_kategorie(self):
        "!! musi byt volano az po kategoriich !!"
        return set(list(self.zavodnici_vsichni())) - set(self.zavodnici_s_kategorii)

class KategoriePoharu(models.Model):
    POHLAVI = (
        ('m', u'muži'),
        ('z', u'ženy'),
    )
    nazev = models.CharField(u'Název', max_length=50)
    znacka = models.CharField(
        u'Značka', max_length=10,
        null=True, blank=True,
        help_text=u'značka kategorie se použije při\
        porovnávání s <b>vnucenými kategoriemi</b> závodníků')
    pohlavi = models.CharField(
        u'Pohlaví', max_length=1, choices=POHLAVI,
        null=True, blank=True)
    vek_od = models.SmallIntegerField(
        u'Věk od', null=True, blank=True,
        help_text=u'věk závodníka včetně')
    vek_do = models.SmallIntegerField(
        u'Věk do', null=True, blank=True,
        help_text=u'věk závodníka včetně')
    poradi = models.SmallIntegerField(
        u'Pořadí', null=True, blank=True)

    atributy = models.ManyToManyField(
        'lide.Atribut', verbose_name=u'Požadované atributy člověka', blank=True
        )
    zavodu = models.SmallIntegerField(
        u'Počet nejlepších výsledků',
        help_text=u'počet nejlepších závodů jež budou započítany,\
        <br>při prázdné kolonce bude použita hodnota poháru',
        blank=True, null=True)
    bod_hodnoceni = models.ForeignKey(
        'BodoveHodnoceni', verbose_name=u'Bodové hodnocení',
        help_text=u'bodová tabulka pro kategorii poháru,<br>\
        při prázdné kolonce bude použita tabulka z poháru',
        related_name='kategorie', on_delete=models.CASCADE,
        blank=True, null=True)
    pohar = models.ForeignKey(
        Pohar, verbose_name=u'pohár',
        related_name='kategorie_poharu')

    class Meta:
        verbose_name = u'Kategorie poháru'
        verbose_name_plural = u'Kategorie pohárů'
        unique_together = (('pohar', 'nazev'),)
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
        return ('pohary:kategorie-poharu_detail', (self.id,))




    def zavodnici(self):
        "vrati zavodniky kategorie serazene dle zavodu/vysledneho_casu"

        def _rozsah_narozeni(rocnik):
            rok = rocnik.datum.year
            # korekce pro sezonu zari-duben
            if rocnik.zavod.korekce_sezony:
                rok += 1
            return (
                rok - (self.vek_do or 200),
                min((rok - (self.vek_od or 0), date.today().year))
            )

        zarazeni = []
        for zavodnik in self.pohar.zavodnici_vsichni():
            vhodny = False
            if zavodnik.kategorie:  # podminka pridana pro pripad dvojich kategorii pro cloveka
                vhodny = zavodnik.kategorie.znacka == self.znacka
            else:
                vhodny = kategorie_test_cloveka(self, zavodnik, _rozsah_narozeni(zavodnik.rocnik))
            if vhodny:
                zarazeni.append(zavodnik)
                self.pohar.zavodnici_s_kategorii.append(zavodnik)
        return zarazeni

    def pocet_zavodu(self):
        return self.zavodu or self.pohar.zavodu or False

    def bodove_hodnoceni(self):
        return self.bod_hodnoceni or self.pohar.bod_hodnoceni

    def poradi_zavodniku(self):
        def _nejlepsi_zavody(zavodnici):
            '''tabulka lidi a jejich opozicovane zavody dle datumu
            {<Clovek: Jirman Jan 2014>:
                [<Zavodnik: Jirman Jan 2014 - Okolo Osta┼íe 2015>,
                <Zavodnik: Jirman Jan 2014 - Okolo Osta┼íe 2016>], ...'''
            lide = {}
            rocnik = None
            i = 1
            for zavodnik in zavodnici:
                if rocnik == zavodnik.rocnik:
                    i += 1
                else:
                    i = 1
                clovek = zavodnik.clovek
                # zapise poradi do attributu zavodnika!
                zavodnik.poradi = i
                lide.setdefault(clovek, [])
                lide[clovek].append(zavodnik)
                rocnik = zavodnik.rocnik

            # oznaceni zapocitavanych zavodu do atributu zavodnika
            for clovek, zavodnici in lide.items():
                zapocitane = sorted(zavodnici, key=attrgetter('poradi'))[:self.pocet_zavodu()]
                for zavodnik in zapocitane:
                    zavodnik.zapocitane = True
            return lide

        def _oboduj_a_serad(lide):
            '''projede lide, oboduje zavody a seradi lidi do listu dle bodu
            [(53 ,Clovek, [zavody,...]),..]'''
            zebricek = []
            body_dict = self.bodove_hodnoceni().hodnoceni_dict()
            for clovek, zavody in lide.items():
                soucet = 0
                # maximum bodu z nejlepsi pozice pro 2.stupen razeni
                maximum = []
                for zavod in zavody:
                    body = body_dict.get(zavod.poradi, 0)
                    zavod.body = body
                    if hasattr(zavod, 'zapocitane'):
                        soucet += body
                        maximum.append(body)
                soucet += sum(
                    [m / 100.0 ** i for i, m in enumerate(sorted(maximum, reverse=True), 2)])
                zebricek.append([clovek, zavody, soucet])
            zebricek = sorted(zebricek, key=lambda x: x[2], reverse=True)
            return zebricek

        def _stejne_body(zebricek):
            '''vyresi lidi se stejnym poctem bodu'''

            def _stejne_soucty(zebricek):
                'vrati slovnik lidi se stejnymi soucty'
                stejne_soucty = {}
                for index, radek in enumerate(zebricek, 0):
                    soucet = radek[2]
                    if soucet == zebricek[index-1][2]:
                        stejne_soucty.setdefault(soucet, [index-1]).append(index)
                return stejne_soucty

            def _vyhral(index):
                'prida cifry k souctu'
                soucet_str = str(zebricek[index][2]) + '1'
                zebricek[index][2] = float(soucet_str)

            # stejne soucty
            for indexy_zebricku in _stejne_soucty(zebricek).values():
                # lide stejneho souctu
                for i_domaci in indexy_zebricku:
                    # ostatni_indexy = list(indexy_zebricku)
                    indexy_zebricku.remove(i_domaci)
                    zavodnici_domaci = zebricek[i_domaci][1]
                    rocniky_domaci = set(z.rocnik for z in zavodnici_domaci)
                    # nyni porovnat zavodniky mezi sebou
                    for i_host in indexy_zebricku:
                        zavodnici_host = zebricek[i_host][1]
                        rocniky_host = set(z.rocnik for z in zavodnici_host)
                        stejne_rocniky = rocniky_domaci.intersection(rocniky_host)
                        for rocnik in stejne_rocniky:
                            cas_domaci = [
                                z for z in zavodnici_domaci if z.rocnik == rocnik][0].vysledny_cas
                            cas_host = [
                                z for z in zavodnici_host if z.rocnik == rocnik][0].vysledny_cas
                            if cas_domaci < cas_host:
                                _vyhral(i_domaci)
                            elif cas_domaci == cas_host:
                                zebricek[i_domaci][0].varovani = 'error'
                                zebricek[i_host][0].varovani = 'error'
                            else:
                                _vyhral(i_host)

            zebricek = sorted(zebricek, key=lambda x: x[2], reverse=True)

            pozice = 1
            for index, radek in enumerate(zebricek, 0):
                if index != 0 and radek[2] < zebricek[index-1][2]:
                    pozice += 1
                zebricek[index].append(pozice)

            for indexy_zebricku in _stejne_soucty(zebricek).values():
                for index in indexy_zebricku:
                    if zebricek[index][0].varovani != 'error':
                        zebricek[index][0].varovani = 'warning'

            return zebricek

        def _doplnit_zavody_nulou(zebricek):
            '''doplneni nezucastnenych zavodu NONE'''
            vsechny_rocniky = list(self.pohar.rocniky_chronologicky())
            novy_zebricek = []
            for clovek, zavody, soucet, pozice in zebricek:
                i_zav = 0
                doplnene_zavody = []
                for rocnik in vsechny_rocniky:
                    try:
                        if zavody[i_zav].rocnik != rocnik:
                            doplnene_zavody.append(None)
                        else:
                            doplnene_zavody.append(zavody[i_zav])
                            i_zav += 1
                    except IndexError:
                        doplnene_zavody.append(None)
                novy_zebricek.append((clovek, doplnene_zavody, soucet, pozice))
            return novy_zebricek


        lide = _nejlepsi_zavody(self.zavodnici())
        zebricek = _oboduj_a_serad(lide)
        zebricek = _stejne_body(zebricek)
        zebricek = _doplnit_zavody_nulou(zebricek)
        return zebricek


class BodoveHodnoceni(models.Model):
    nazev = models.CharField(u'Název', max_length=50)
    hodnoceni = models.TextField(
        u'Hodnocení prvních pozic',
        help_text=u'formát:<br>1-50<i>(enter)</i><br>2-47<br>3-44')
    info = models.TextField(u'Informace', blank=True, null=True)

    class Meta:
        verbose_name = u'Bodové hodnocení pozic'
        verbose_name_plural = u'Bodová hodnocení pozic'

    def __unicode__(self):
        return self.nazev

    def hodnoceni_dict(self):
        '''rozparsuje body do slovniku, doplni zbytek pozic'''
        dvojice = self.hodnoceni.split('\n')
        body = {}
        for dvoj in dvojice:
            poradi, bod = dvoj.split('-')
            poradi = int(poradi)
            bod = int(bod)
            body[poradi] = bod
        bod -= 1
        poradi += 1
        while bod > 0:
            body[poradi] = bod
            bod -= 1
            poradi += 1
        return body
