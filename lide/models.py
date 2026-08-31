from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.text import slugify

POHLAVI = (
    ('', '---'),
    ('m', 'muž'),
    ('z', 'žena'),
)


def _get_sorting_slug(slovo):

    """ Vrati upraveny sorting slug,
    napomaha razeni slov (jmena, nazvy klubu) s diakritikou.
    Nahradi pismena s diakritikou spojenim se Z
    """

    slovo = slovo.upper()
    vysledek = ''
    for pismeno in slovo:
        vysledek += pismeno
        if pismeno in 'ĚŠČŘŽÝÁÍÉŤĎŇÓÚŮÜÖËŁ':
            vysledek += 'Z'
    return slugify(vysledek)


class Stat(models.Model):

    """ Statni prislusnost cloveka
    """

    nazev = models.CharField('Název', max_length=30, unique=True, blank=True)
    zkratka = models.SlugField(unique=True, blank=True)
    poradi = models.PositiveSmallIntegerField('Pořadí', default=100, help_text='určuje pořadí států v nabídkách')

    class Meta:
        verbose_name = 'Stát'
        verbose_name_plural = 'Státy'
        ordering = ('poradi', 'zkratka', 'nazev')

    def __str__(self):
        return f'{self.nazev} ({self.zkratka})'
    

class Clovek(models.Model):

    """ Clovek
    - clovek je pres Clenstvi spojen s Klubem
    - pres Zavodnika je spojen s Rocnikem a Kategorii
    """

    jmeno = models.CharField('Křestní jméno', max_length=20)
    prijmeni = models.CharField('Příjmení', max_length=30)
    pohlavi = models.CharField(
        'Pohlaví', max_length=1,
        choices=POHLAVI,
        null=True, blank=True)
    stat = models.ForeignKey(
        'Stat', verbose_name='Stát', related_name='lidi',
        on_delete=models.SET_NULL, null=True)
    narozen = models.PositiveSmallIntegerField('Narozen(a)')
    jmeno_slug = models.SlugField(editable=False, unique=False, blank=True)
    prijmeni_slug = models.SlugField(editable=False, unique=False, blank=True)
    slug = models.SlugField(db_index=True, unique=True, blank=True)
    prijmeni_slug_sorting = models.SlugField(editable=False, unique=False)
    varovani = None


    class Meta:
        verbose_name = 'Člověk'
        verbose_name_plural = 'Lidé'
        ordering = ('prijmeni_slug_sorting', 'jmeno_slug')
        unique_together = ('jmeno', 'prijmeni', 'narozen')


    def __str__(self):
        return f'{self.prijmeni} {self.jmeno} {self.narozen}'


    def get_absolute_url(self, user=None):
        if user and user.is_active:
            return reverse('lide:clovek_update', args=(self.slug,))
        else:
            return reverse('lide:clovek_detail', args=(self.slug,))


    def save(self, *args, **kwargs):

        """
        Ulozeni cloveka
        - pohlavi: pokud neni nastaveno, tak ho odhadne z prijmeni
        - nastaveni vsech slugu
        """

        if not self.pohlavi:
            self.pohlavi = 'z' if self.prijmeni[-1] == 'á' else 'm'
        elif self.pohlavi not in POHLAVI:
            self.pohlavi = 'm' if self.pohlavi[0].lower() == 'm' else 'z'
        self.prijmeni_slug = slugify(self.prijmeni)
        self.prijmeni_slug_sorting = self.prijmeni_slug
        self.prijmeni_slug_sorting = _get_sorting_slug(self.prijmeni)
        self.jmeno_slug = slugify(self.jmeno)
        super().save(*args, **kwargs)  # nejprve ulozi pro zjisteni ID
        self.slug = f'{self.prijmeni_slug}-{self.jmeno_slug}-{self.narozen!s}_{self.id!s}'
        return super().save(update_fields=['slug']) #updatuje SLUG


    def cele_jmeno(self):
        return f'{self.prijmeni} {self.jmeno}'


    def serazene_clenstvi_pro_zavod(self, zavod):

        """ Vraci serazeny queryset clenstvi v klubech
        dle dulezitosti pro dany `Zavod`
        """

        vhodne_clenstvi = self.clenstvi.filter(
            Q(sport=zavod.sport) | Q(sport__isnull=True)
        ).order_by('-sport', '-priorita')
        if not vhodne_clenstvi:
            vhodne_clenstvi = self.clenstvi.all().order_by('-priorita')
        return vhodne_clenstvi


    def jednotlive_kluby(self):

        """ Vrati set Klubu cloveka """

        from kluby.models import Klub
        return set(Klub.objects.filter(clenstvi__clovek=self))


class Clenstvi(models.Model):

    """ Clenstvi
    - propojeni cloveka, klubu a sportu,
    - mezi clovekem a klubem je vztah m2m
    - Clenstvi je pouzito pouze pro nabidnuti klubu u vkladani zavodnika, neni na nej nic natvrdo navazano
    """

    clovek = models.ForeignKey(
        'Clovek',
        verbose_name='člověk', related_name='clenstvi',
        on_delete=models.CASCADE)
    klub = models.ForeignKey(
        'kluby.Klub',
        verbose_name='klub', related_name='clenstvi',
        on_delete=models.CASCADE)
    sport = models.ForeignKey(
        'zavody.Sport',
        on_delete=models.SET_NULL,
        null=True, blank=True)
    priorita = models.SmallIntegerField(
        'Priorita', null=True, blank=True,
        help_text='určuje prioritu klubů se stejným sportem - větší číslo vyhrává !')

    class Meta:
        verbose_name = 'Členství v klubu'
        verbose_name_plural = 'Členství v klubech'
        ordering = ('clovek', '-sport', '-priorita')
        unique_together = ('clovek', 'klub', 'sport')


    def __str__(self):
        return f'{self.clovek} - {self.klub}'
