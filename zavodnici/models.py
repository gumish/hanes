import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, Max, Q, F
from django.urls import reverse


class Zavodnik(models.Model):

    """ Zavodnik
    - propojeni Cloveka, Rocniku a Kategorie
    """

    # nastavena pozdeji v modelu Kategorie, casova ztrata na prvniho
    casova_ztrata = None

    NEDOKONCIL = (
        ('DNS', 'DNS'),
        ('DNF', 'DNF'),
        ('DSQ', 'DSQ'),
        ('DNP', 'DNP'),
    )

    rocnik = models.ForeignKey(
        'zavody.Rocnik',
        verbose_name='ročník závodu', related_name='zavodnici',
        on_delete=models.CASCADE)
    clovek = models.ForeignKey(
        'lide.Clovek',
        verbose_name='člověk', related_name='zavodnici',
        null=True, blank=True,  # kvuli docasnym neznamym zavodnikum
        on_delete=models.CASCADE)
    cislo = models.CharField(
        'Startovní číslo',
        max_length=10,
        null=True, blank=True,
        help_text='číslo je unikátní pro daný ročník - hlídáno')
    klub = models.ForeignKey(
        'kluby.Klub',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='klub',
        related_name='zavodnici')
    kategorie = models.ForeignKey(
        'zavody.Kategorie',
        db_index=True,
        help_text='vnucená kategorie, která ruší automatické přiřazení',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='kategorie natvrdo',
        related_name='zavodnici')
    kategorie_temp = models.ForeignKey(
        'zavody.Kategorie',
        db_index=True,
        help_text='dočasná kategorie systému',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        # editable=False,
        verbose_name='kategorie dočasná',
        related_name='zavodnici_temp')

    startovni_cas = models.TimeField(
        'Startovní čas', null=True, blank=True,
        help_text='pokud je zadán, pak se výsledný čas počítá z rozdílu časů start-cíl')
    cilovy_cas = models.TimeField(
        'Cílový čas',
        null=True, blank=True,
        help_text='pokud není zadán `startovní čas`, pak se jedná o výsledný čas závodu')
    vysledny_cas = models.DurationField(
        'Výsledný čas',
        null=True, blank=True, editable=False)
    nedokoncil = models.CharField(
        'Nedokončil', null=True, blank=True,
        choices=NEDOKONCIL, max_length=10)
    odstartoval = models.BooleanField(
        'Odstartoval', default=None, null=True,
        help_text='pouze informační hodnota od startéra, že závodník opravdu odstartoval')
    info = models.CharField('Info', max_length=256, null=True, blank=True)

    class Meta:
        verbose_name = 'Závodník'
        verbose_name_plural = 'Závodníci'
        ordering = (
            'rocnik',
            'vysledny_cas',
            F('startovni_cas').asc(nulls_last=True),
            'cislo')


    def __str__(self):
        return '{0} - {1}'.format(self.clovek or '???', self.rocnik)


    def clean(self):

        """ Uprava a validace `unique_together` pred ulozenim
        - pokud uz clovek zavodi v tomto zavode nahlasit chybu
        """

        # pokud uz je zavodnik v databazi ulozen, pak ho vynechat z querysetu
        zavodnici_rocniku = Zavodnik.objects.filter(rocnik=self.rocnik)
        if self.pk:
            zavodnici_rocniku = zavodnici_rocniku.exclude(pk=self.pk)

        ## NA PRANI 2020-06-26 VALIDACE ZRUSENA
        # zavodi tento clovek uz v tomto zavode?
        # duplicity_cloveka = (
        #     zavodnici_rocniku
        #     .filter(clovek=self.clovek)
        #     .filter(
        #         Q(kategorie=self.kategorie) |
        #         Q(kategorie_temp=self.kategorie))
        #     .order_by('-kategorie_temp'))
        # if duplicity_cloveka:
        #     raise ValidationError({
        #         'clovek':
        #             '''"{0}" již v tomto ročníku závodí<br>v kategorii "{1}"<br><br>
        #             Závodníka nelze přidat, nebo mu natvrdo přiřaďte jinou kategorii'''.format(
        #                 self.clovek,
        #                 duplicity_cloveka[0].kategorie_temp
        #             )
        #     })

        # zavodi jiz toto cislo?
        if self.cislo:
            duplicity_cisla = zavodnici_rocniku.filter(cislo=self.cislo)
            if duplicity_cisla:
                raise ValidationError({
                    'cislo': 'S číslem "{0}" již závodí<br>"{1}"'.format(
                        self.cislo,
                        duplicity_cisla[0].clovek
                    )
                })

        # STARTOVNI_CAS <= CILOVY_CAS
        # if self.startovni_cas and self.cilovy_cas:
        #     if not (self.kategorie_temp.spusteni_stopek + self.cilovy_cas >= self.startovni_cas):
        #         raise ValidationError({
        #             'startovni_cas': u'Startovní čas musí být menší než cílový čas!',
        #             'cilovy_cas': u'Cílový čas musí být větší než startovní čas!',
        #         })


    def get_absolute_url(self):
        return reverse('zavodnici:editace_zavodnika', args=(self.id,))


    def save(self, nekontroluj=False, *args, **kwargs):

        """ Ulozeni zavodnika
        - pokud dochazi ke kontrole (nekontroluj=False), pak:
            - pokud je zadan klub, pak se u nej nastavi vyssi 'priorita' nez 'priorita' pro tento sport u jinych klubu
            - 'startovni_cas' nastavit na None
            - vypocet 'vysledneho_casu'
        - nastaveni atributu 'odstartoval' a 'nedokoncil'
        """

        if not nekontroluj:
            # KLUBY / CLENSTVI + SPORT
            from lide.models import Clenstvi
            if self.klub:
                max_priorita_jinych_klubu = (
                    Clenstvi.objects
                    .filter(
                        clovek=self.clovek,
                        sport=self.rocnik.zavod.sport)
                    .exclude(klub=self.klub)
                    .aggregate(Max('priorita'))
                    ['priorita__max'] or 0
                )
                clenstvi, _created = Clenstvi.objects.get_or_create(
                    clovek=self.clovek,
                    klub=self.klub,
                    sport=self.rocnik.zavod.sport)
                clenstvi.priorita = max_priorita_jinych_klubu + 1
                clenstvi.save()

            # CASY
            if not self.startovni_cas:
                self.startovni_cas = None
            if self.cilovy_cas:
                # (17.11.2016) TRY/EXCEPT: pokud neexistuje kategorie u docasneho zavodnika
                try:
                    spusteni_stopek = self.kategorie_temp.spusteni_stopek
                    if not spusteni_stopek:
                        spusteni_stopek = datetime.time(0, 0, 0)
                except:
                    spusteni_stopek = datetime.time(0, 0, 0)
                # print(spusteni_stopek)
                self.vysledny_cas = (
                    # C) CILOVY CAS 00:30:00
                    datetime.timedelta(
                        hours=self.cilovy_cas.hour,
                        minutes=self.cilovy_cas.minute,
                        seconds=self.cilovy_cas.second,
                        microseconds=self.cilovy_cas.microsecond
                    ) - (
                        # B) STARTOVNI CAS 10:10:00
                        datetime.datetime.combine(
                            datetime.date.today(),
                            self.startovni_cas or datetime.time(0, 0, 0)
                        ) -
                        # A) SPUSTENI STOPEK 10:00:00
                        datetime.datetime.combine(
                            datetime.date.today(),
                            spusteni_stopek
                        )
                    )
                    # VYSLEDNY CAS A-B+C  00:20:00
                )
            else:
                self.vysledny_cas = None

        # ODSTARTOVAL - NEDOKONCIL
        if self.odstartoval is False:
            self.nedokoncil = 'DNS'
        elif self.odstartoval is True and self.nedokoncil == 'DNS':
            self.nedokoncil = None
        super(Zavodnik, self).save(*args, **kwargs)

    def poradi_v_kategorii(self):
        if self.kategorie_temp and self.vysledny_cas and not self.nedokoncil:
            lepsich = (
                Zavodnik.objects
                .filter(
                    rocnik=self.rocnik,
                    kategorie_temp=self.kategorie_temp,
                    vysledny_cas__lt=self.vysledny_cas,
                )
                .aggregate(pocet=Count('vysledny_cas'))
            )
            return str(lepsich['pocet'] + 1) + '.'
        else:
            return None

    def poradi_na_trati(self):
        if self.kategorie_temp and self.kategorie_temp.delka_trate and self.vysledny_cas and not self.nedokoncil:
            lepsich = Zavodnik.objects.filter(
                rocnik=self.rocnik,
                kategorie_temp__delka_trate=self.kategorie_temp.delka_trate,
                vysledny_cas__lt=self.vysledny_cas,
                ).aggregate(pocet=Count('vysledny_cas'))
            return str(lepsich['pocet'] + 1) + '.'
        else:
            return None

    def zavodniku_na_trati(self):
        if self.kategorie_temp and self.kategorie_temp.delka_trate:
            return Zavodnik.objects.filter(
                rocnik=self.rocnik,
                kategorie_temp__delka_trate=self.kategorie_temp.delka_trate).count()
        else:
            return None
