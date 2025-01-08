from datetime import date, timedelta
from functools import cache, cached_property
from operator import attrgetter

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from zavodnici.models import Zavodnik
from zavody.models import kategorie_test_cloveka


class Pohar(models.Model):

    # list pouzit pro fci 'Pohar.zavodnici_bez_kategorie()'
    zavodnici_s_kategorii = []

    nazev = models.CharField("Název", max_length=50)
    datum = models.DateField("Datum pořádání")
    slug = models.SlugField(editable=False, unique=True)
    info = models.TextField("Info", null=True, blank=True)
    zavodu = models.SmallIntegerField(
        "Počet nejlepších výsledků všech sportů",
        help_text="defaultní počet nejlepších výsledků pro všechny sporty jež budou do poháru započítany, při prázdné kolonce budou použity všechny závody",
        blank=True, null=True,
    )
    bod_hodnoceni = models.ForeignKey(
        "BodoveHodnoceni",
        verbose_name="Bodové hodnocení",
        help_text="bodová tabulka pro pohár, bude použita v případě nespecifikované tabulky u kategorie, v případě prázdného kolonky se boduje postupně odzadu",
        related_name="pohary",
        on_delete=models.CASCADE,
        blank=True, null=True,
    )
    rocniky = models.ManyToManyField(
        "zavody.Rocnik", verbose_name="Ročníky", related_name="pohary"
    )
    kluby = models.ManyToManyField(
        "kluby.Klub",
        verbose_name="Kluby",
        related_name="pohary",
        blank=True,
        help_text="pokud není zadán žádný Klub, pak se použijí všechny",
    )

    class Meta:
        verbose_name = "Pohár"
        verbose_name_plural = "Poháry"
        ordering = ("-datum",)
        unique_together = ("nazev", "datum")

    def __str__(self):
        return self.nazev

    def get_absolute_url(self):
        return reverse("pohary:pohar_detail", args=(self.slug,))

    def get_delete_url(self):
        return ("pohary:pohar_smazani", (self.slug,))

    def save(self, *args, **kwargs):
        self.slug = "{0}_{1}".format(slugify(self.nazev), self.datum.year)
        return super(Pohar, self).save(*args, **kwargs)

    def rocniky_chronologicky(self):
        return self.rocniky.all().order_by("datum")

    def prvni_rocnik(self):
        return self.rocniky_chronologicky().first()

    @cached_property
    def zavodnici_vsichni(self):
        zavodnici = Zavodnik.objects.filter(
            rocnik__in=self.rocniky.all(), vysledny_cas__isnull=False, nedokoncil=None
        )

        # pokud je zadáno kluby, pak se použijí jen tyto Kluby
        if self.kluby.exists():
            zavodnici = zavodnici.filter(klub__in=self.kluby.all())

        return zavodnici.select_related('rocnik', 'klub').prefetch_related('clovek').order_by("rocnik__datum", "vysledny_cas")


    def zavodnici_bez_kategorie(self):
        """
        Musi byt volano az po kategoriich,
        tak aby se nejprve naplnila vlastnost 'Pohar.zavodnici_s_kategorii' !!
        """
        return set(list(self.zavodnici_vsichni)) - set(self.zavodnici_s_kategorii)


class KategoriePoharu(models.Model):
    POHLAVI = (
        ("m", "muži"),
        ("z", "ženy"),
    )
    nazev = models.CharField("Název", max_length=50)
    znacka = models.CharField(
        "Značka",
        max_length=10,
        null=True, blank=True,
        help_text="značka kategorie se použije při porovnávání s vnucenými kategoriemi závodníků",
    )
    pohlavi = models.CharField(
        "Pohlaví", max_length=1, choices=POHLAVI, null=True, blank=True
    )
    vek_od = models.SmallIntegerField(
        "Věk od", null=True, blank=True, help_text="věk závodníka včetně"
    )
    vek_do = models.SmallIntegerField(
        "Věk do", null=True, blank=True, help_text="věk závodníka včetně"
    )
    poradi = models.SmallIntegerField("Pořadí", null=True, blank=True)
    zavodu = models.SmallIntegerField(
        "Počet nejlepších výsledků",
        help_text="počet nejlepších závodů jež budou započítany, při prázdné kolonce bude použita hodnota poháru",
        blank=True, null=True,
    )
    bod_hodnoceni = models.ForeignKey(
        "BodoveHodnoceni",
        verbose_name="Bodové hodnocení",
        related_name="kategorie",
        help_text="bodová tabulka pro kategorii poháru, při prázdné kolonce bude použita tabulka z poháru",
        on_delete=models.CASCADE,
        blank=True, null=True,
    )
    pohar = models.ForeignKey(
        Pohar,
        verbose_name="pohár",
        related_name="kategorie_poharu",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "Kategorie poháru"
        verbose_name_plural = "Kategorie pohárů"
        unique_together = (("pohar", "nazev"),)
        ordering = ("poradi", "id")

    def __str__(self):
        popis = "{0} - {1}".format(self.nazev, self.get_pohlavi_display() or "unisex")
        if self.znacka:
            popis = self.znacka + " - " + popis
        if self.vek_od or self.vek_do:
            popis += " / {0}-{1}".format(self.vek_od or "?", self.vek_do or "?")
        return popis

    def get_absolute_url(self):
        return reverse("pohary:kategorie-poharu_detail", args=(self.id,))

    def zavodnici(self):
        """
        Prefiltruje vsechny zavodniky 'Poharu' a vrati pouze ty, co patri do 'KategoriePoharu'.
        Pokud je vhodny, pak je zarazen do vysledneho listu,
        a je pridan do listu vlastnosti 'Pohar.zavodnici_s_kategorii'

        Returns:
            zarazeni(list) - list zavodniku kategorie serazene dle zavodu/vysledneho_casu
        """

        def _rozsah_narozeni(rocnik):
            """
            Vrati tuple rozsahu roku narozeni zavodniku pro tuto kategorii
            """
            rok = rocnik.datum.year
            # korekce pro sezonu zari-duben
            if rocnik.zavod.korekce_sezony:
                rok += 1
            return (
                rok - (self.vek_do or 200),
                min((rok - (self.vek_od or 0), date.today().year)),
            )

        zarazeni = []
        for zavodnik in self.pohar.zavodnici_vsichni:
            vhodny = False
            if (
                zavodnik.kategorie
            ):  # podminka pridana pro pripad dvojich kategorii pro cloveka
                vhodny = zavodnik.kategorie.znacka == self.znacka
            else:
                vhodny = kategorie_test_cloveka(
                    self, zavodnik, _rozsah_narozeni(zavodnik.rocnik)
                )
            if vhodny:
                zarazeni.append(zavodnik)
                self.pohar.zavodnici_s_kategorii.append(zavodnik)
        return zarazeni

    def bodove_hodnoceni(self):
        """
        Vrati pocet zavodu, ktere jsou pocitany do poharu
        """
        return self.bod_hodnoceni or self.pohar.bod_hodnoceni


    def poradi_zavodniku(self) -> list:
        """
        1. Upraví pořadí závodníka na základě jeho výkonu a roku.
        2. Přidá závodníka do slovníku lidí.
        3. Označí závody, které se započítají do poháru.
        4. Vrátí slovník lidí a jejich závodníků s nejlepšími závody.
        5. Projede slovník lidí, oboduje závody a seřadí lidi do listu dle bodů.
        6. Vyřeší lidi se stejným počtem bodů.
        7. Doplní nezúčastněné závody hodnotou None.
        8. Vrátí list: Seřazený žebříček závodníků ve formátu [(pozice, Clovek, [zavody,...]),...]
        """

        def _uprav_poradi_zavodnika(zavodnik, rocnik, i, umisteni, minuly_cas) -> tuple:
            """ Upraví pořadí závodníka na základě jeho výkonu a roku.

                Args:
                    zavodnik: Objekt reprezentující závodníka, který by měl mít atributy `rocnik` a `vysledny_cas`.
                    rocnik: Aktuální rok soutěže.
                    i: Aktuální index nebo pozice v pořadí.
                    umisteni: Aktuální pořadí závodníka.
                    minuly_cas: Předchozí zaznamenaný čas závodníka.

                Returns:
                    tuple: N-tice obsahující aktualizované hodnoty pro rocnik, i, umisteni a minuly_cas.
            """
            if rocnik == zavodnik.rocnik:
                i += 1
                if minuly_cas < zavodnik.vysledny_cas:
                    umisteni = i
                elif minuly_cas == zavodnik.vysledny_cas:
                    pass
            else:
                i = 1
                umisteni = 1
                minuly_cas = timedelta()
                rocnik = zavodnik.rocnik
            zavodnik.poradi = umisteni
            minuly_cas = zavodnik.vysledny_cas
            return rocnik, i, umisteni, minuly_cas

        def _pridej_zavodniky_lidem(lide: dict, zavodnik: Zavodnik) -> dict:
            """
            Přidá závodníka do odpovídající osoby ve slovníku.

            Tato funkce vezme slovník lidí a objekt závodníka,
            a přidá závodníka do seznamu závodníků pro odpovídající osobu.

            Args:
                lide (dict): Slovník, kde klíčem je osoba a hodnotou je seznam závodníků.
                zavodnik (Zavodnik): Objekt závodníka, který obsahuje odkaz na osobu.

            Returns:
                dict: Aktualizovaný slovník s přidaným závodníkem k odpovídající osobě.
            """
            clovek = zavodnik.clovek
            lide.setdefault(clovek, [])
            lide[clovek].append(zavodnik)
            return lide

        def _oznac_zapocitane_zavody(lide: dict):
            """
            Označí závody, které se započítají do poháru pro každou osobu ve slovníku.
            Args:
                lide (dict): Slovník, kde klíčem je identifikátor osoby a hodnotou je list závodníků.
                            Každý závodník musí mít atribut 'poradi', který udává pořadí závodu.
            Funkce seřadí závodníky pro každého člověka podle atributu 'poradi' a označí nejlepší závody (až do počtu
            defaultni_pocet_zavodu = self.zavodu nebo self.pohar.zavodu) jako započítané nastavením jejich atributu 'zapocitane' na True.
            Pokud závody poháru obsahují více sportů (např. běh a lyžování), pak se množství započítaných závodů pro každý sport odvíjí od hodnot defaultni_pocet_zavodu.
            Pokud je defaultni_pocet_zavodu False, pak se započítají všechny závody.
            Pokud má pohár nějaké related pohar.pocet_zavodu_sportu, pak se pro každý sport použije jeho hodnota zavodu.
            """
            defaultni_pocet_zavodu = self.zavodu or self.pohar.zavodu or False

            for zavodnici_cloveka in lide.values():
                serazeni_zavodnici_dle_poradi = sorted(zavodnici_cloveka, key=attrgetter("poradi"))  # atribut 'poradi' je nastaven v '_uprav_poradi_zavodnika()'

                # Získání počtu závodů pro každý sport objevený se v poháru
                sport_pocet_zavodu = {}
                for zavodnik in serazeni_zavodnici_dle_poradi:
                    sport = zavodnik.sport
                    if sport not in sport_pocet_zavodu:
                        pocet_zavodu_poharu_sportu = PocetZavoduPoharuSportu.objects.filter(pohar=self.pohar, sport=sport).first()
                        if pocet_zavodu_poharu_sportu:
                            sport_pocet_zavodu[sport] = pocet_zavodu_poharu_sportu.zavodu
                        else:
                            sport_pocet_zavodu[sport] = defaultni_pocet_zavodu

                # Označení započítaných závodů
                for sport, pocet_zavodu in sport_pocet_zavodu.items():
                    zavodnici_sportu = [z for z in serazeni_zavodnici_dle_poradi if z.sport == sport]
                    for zavodnik in zavodnici_sportu[:pocet_zavodu]:
                        zavodnik.zapocitane = True

        def _get_lide_s_nejlepsimi_zavody(zavodnici: list) -> dict:
            """
            Zpracuje seznam závodníků a vrátí slovník lidí s jejich nejlepšími závody.
            Args:
                zavodnici (list): Seznam závodníků.
            Returns:
                dict: Slovník, kde klíče jsou lidé a hodnoty jsou jejich nejlepší závody.
            """
            lide = {}
            rocnik = None
            i = 1
            umisteni = 1
            minuly_cas = timedelta()

            for zavodnik in zavodnici:
                rocnik, i, umisteni, minuly_cas = _uprav_poradi_zavodnika(zavodnik, rocnik, i, umisteni, minuly_cas)
                lide = _pridej_zavodniky_lidem(lide, zavodnik)

            _oznac_zapocitane_zavody(lide)
            return lide


        def _oboduj_a_serad(lide):
            """
            Projede slovnik lide, oboduje zavody a seradi lidi do listu dle bodu

            Attrs:
                lide(dict) - slovnik lidi a jejich zavodniku z '_get_lide_s_nejlepsimi_zavody()'
            Returns:
                zebricek(list) - [(53 ,Clovek, [zavody,...]),..]
            """
            zebricek = []
            # slovnik bodu za poradi v zavodu
            body_za_poradi = self.bodove_hodnoceni().hodnoceni_dict()
            for clovek, zavody in list(
                lide.items()
            ):  # pro zjednoduseni zavodnici => zavody
                soucet = 0
                # maximum bodu z nejlepsi pozice pro 2.stupen razeni
                maximum = []
                for zavod in zavody:
                    body = body_za_poradi.get(zavod.poradi, 0)
                    zavod.body = body
                    if hasattr(zavod, "zapocitane"):
                        soucet += body
                        maximum.append(body)
                soucet += sum(
                    [
                        m / 100.0**i
                        for i, m in enumerate(sorted(maximum, reverse=True), 2)
                    ]
                )
                zebricek.append([clovek, zavody, soucet])
            zebricek = sorted(zebricek, key=lambda x: x[2], reverse=True)
            return zebricek

        def _stejne_body(zebricek: list) -> list:
            """
            Zpracuje žebříček závodníků a řeší případy shodných bodů porovnáním časů jednotlivých závodníků.
                Args:
                    zebricek (list): Seznam seznamů, kde každý vnitřní seznam představuje data závodníka.
                                    Každý vnitřní seznam by měl obsahovat alespoň tři prvky:
                                    - Objekt s atributem 'varovani'.
                                    - Seznam závodníků, z nichž každý má atributy 'rocnik' a 'vysledny_cas'.
                                    - Číselné skóre.
                Returns:
                    list: Zpracovaný žebříček s aktualizovanými skóre a pozicemi a varováními pro případy shod.
            """

            def _stejne_soucty(zebricek):
                "vrati slovnik lidi se stejnymi soucty"
                stejne_soucty = {}
                for index, radek in enumerate(zebricek, 0):
                    soucet = radek[2]
                    if soucet == zebricek[index - 1][2]:
                        stejne_soucty.setdefault(soucet, [index - 1]).append(index)
                return stejne_soucty

            def _vyhral(index):
                "prida cifry k souctu"
                soucet_str = str(zebricek[index][2]) + "1"
                zebricek[index][2] = float(soucet_str)

            # stejne soucty
            for indexy_zebricku in list(_stejne_soucty(zebricek).values()):
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
                                z for z in zavodnici_domaci if z.rocnik == rocnik
                            ][0].vysledny_cas
                            cas_host = [
                                z for z in zavodnici_host if z.rocnik == rocnik
                            ][0].vysledny_cas
                            if cas_domaci < cas_host:
                                _vyhral(i_domaci)
                            elif cas_domaci == cas_host:
                                zebricek[i_domaci][0].varovani = "error"
                                zebricek[i_host][0].varovani = "error"
                            else:
                                _vyhral(i_host)

            zebricek = sorted(zebricek, key=lambda x: x[2], reverse=True)

            # prirazeni finalnich pozic dle bodu
            pozice = 1
            skok_pozic = 1
            for index, radek in enumerate(zebricek, 0):
                # u prvniho zavodnika se nic nepocita
                if index != 0:
                    # pokud ma zavodnik vice bodu nez ten predesli zvys pozici o skok ..
                    if radek[2] < zebricek[index - 1][2]:
                        pozice += skok_pozic
                        skok_pozic = 1
                    # .. pokud maji stejne, pak navysej pouze skok, o ktery se zvysi pozice pri nasledne zmene bodu
                    else:
                        skok_pozic += 1
                zebricek[index].append(pozice)

            for indexy_zebricku in list(_stejne_soucty(zebricek).values()):
                for index in indexy_zebricku:
                    if zebricek[index][0].varovani != "error":
                        zebricek[index][0].varovani = "warning"

            return zebricek

        def _doplnit_zavody_nulou(zebricek):
            """
            doplneni nezucastnenych zavodu NONE
            """
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

        lide = _get_lide_s_nejlepsimi_zavody(self.zavodnici())
        zebricek = _oboduj_a_serad(lide)
        zebricek = _stejne_body(zebricek)
        zebricek = _doplnit_zavody_nulou(zebricek)
        return zebricek


class BodoveHodnoceni(models.Model):
    """
    Tabulka bodovych hodnoceni prvnich pozic.
    Pres FK je spojen s 'Poharem' nebo 'KategoriiPoharu'
    """

    nazev = models.CharField("Název", max_length=50)
    hodnoceni = models.TextField(
        "Hodnocení prvních pozic",
        help_text="formát: 1-50<i>(enter)</i> 2-47 3-44",
    )
    info = models.TextField("Informace", blank=True, null=True)

    class Meta:
        verbose_name = "Bodové hodnocení pozic"
        verbose_name_plural = "Bodová hodnocení pozic"

    def __str__(self):
        return self.nazev

    def hodnoceni_dict(self):
        """
        Rozparsuje body do slovniku {(poradi: body)}, doplni zbytek pozic
        Returns:
            body(dict) - {1: 50, 2: 47, 3: 44, ...}
        """
        dvojice = self.hodnoceni.split("\n")
        body = {}
        for dvoj in dvojice:
            poradi, bod = dvoj.split("-")
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


class PocetZavoduPoharuSportu(models.Model):
    """
    Vyjimky poctu zavodu (vysledku), ktere se zapocitaji do poharu, pro dany Sport.
    Ostatni sporty pouziji defaultni hodnotu z 'Pohar.zavodu'
    """

    pohar = models.ForeignKey(
        Pohar, verbose_name="Pohár",
        related_name="pocet_zavodu_sportu", on_delete=models.CASCADE,
    )
    sport = models.ForeignKey(
        "zavody.Sport", verbose_name="Sport",
        related_name="pocet_zavodu_poharu", on_delete=models.CASCADE
    )
    zavodu = models.PositiveSmallIntegerField(
        "Počet nejlepších výsledků konkrétního sportu",
        help_text="počet nejlepších výsledků konkrétního sportu jež budou do poháru započítany, při prázdné kolonce budou použity všechny závody",
        blank=True, null=True
    )

    class Meta:
        verbose_name = "Počet závodů pro sport"
        verbose_name_plural = "Počty závodů pro sport"
        unique_together = ("pohar", "sport")

    def __str__(self):
        return f"{self.pohar} - {self.sport}"