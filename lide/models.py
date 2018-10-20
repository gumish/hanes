# coding: utf-8

from django.db import models
from django.db.models import Q
from django.utils.text import slugify

POHLAVI = (
    ('', u'---'),
    ('m', u'muž'),
    ('z', u'žena'),
)


def _get_sorting_slug(slovo):

    """ Vrati upraveny sorting slug,
    napomaha razeni slov (jmena, nazvy klubu) s diakritikou.
    Nahradi pismena s diakritikou spojenim se Z
    """

    slovo = slovo.upper()
    vysledek = u''
    for pismeno in slovo:
        vysledek += pismeno
        if pismeno in u'ĚŠČŘŽÝÁÍÉŤĎŇÓÚŮÜÖËŁ':
            vysledek += u'Z'
    return slugify(vysledek)


class Clovek(models.Model):
    jmeno = models.CharField(u'Křestní jméno', max_length=20)
    prijmeni = models.CharField(u'Příjmení', max_length=30)
    pohlavi = models.CharField(
        u'Pohlaví', max_length=1,
        choices=POHLAVI,
        null=True, blank=True)
    narozen = models.PositiveSmallIntegerField(u'Narozen(a)')
    atributy = models.ManyToManyField(
        'Atribut',
        verbose_name=u'Atributy člověka',
        # null=True,
        blank=True
        )
    jmeno_slug = models.SlugField(editable=False, unique=False, blank=True)
    prijmeni_slug = models.SlugField(editable=False, unique=False, blank=True)
    slug = models.SlugField(db_index=True, unique=True, blank=True)
    prijmeni_slug_sorting = models.SlugField(editable=False, unique=False)
    varovani = None


    class Meta:
        verbose_name = u'Člověk'
        verbose_name_plural = u'Lidé'
        ordering = ('prijmeni_slug_sorting', 'jmeno_slug')
        unique_together = ('jmeno', 'prijmeni', 'narozen')


    def __unicode__(self):
        return u'{0} {1} {2}'.format(self.prijmeni, self.jmeno, self.narozen)


    @models.permalink
    def get_absolute_url(self, user=None):
        if user and user.is_active:
            return ('lide:clovek_update', (self.slug,))
        else:
            return ('lide:clovek_detail', (self.slug,))


    def save(self, *args, **kwargs):

        """
        Ulozeni cloveka
        - pohlavi: pokud neni nastaveno, tak ho odhadne z prijmeni
        - nastaveni vsech slugu
        """

        if not self.pohlavi:
            self.pohlavi = 'z' if self.prijmeni[-1] == u'á' else 'm'
        elif self.pohlavi not in POHLAVI:
            self.pohlavi = 'm' if self.pohlavi[0].lower() == 'm' else 'z'
        self.prijmeni_slug = slugify(self.prijmeni)
        self.prijmeni_slug_sorting = self.prijmeni_slug
        self.prijmeni_slug_sorting = _get_sorting_slug(self.prijmeni)
        self.jmeno_slug = slugify(self.jmeno)
        super(Clovek, self).save(*args, **kwargs)  #nejprve ulozi pro zjisteni ID
        self.slug = '{}-{}-{}_{}'.format(
            self.prijmeni_slug, self.jmeno_slug, str(self.narozen), str(self.id))
        return super(Clovek, self).save(update_fields=['slug']) #updatuje SLUG


    def cele_jmeno(self):
        return u'{0} {1}'.format(self.prijmeni, self.jmeno)


    def serazene_clenstvi_pro_zavod(self, zavod):
        'vraci serazeny seznam clenstvi v klubech dle dulezitosti pro dany `zavod`'
        vhodne_clenstvi = self.clenstvi.filter(
            Q(sport=zavod.sport) | Q(sport__isnull=True)
        ).order_by('-sport', '-priorita')
        if not vhodne_clenstvi:
            vhodne_clenstvi = self.clenstvi.all().order_by('-priorita')
        return vhodne_clenstvi


    def jednotlive_kluby(self):
        from kluby.models import Klub
        return set(Klub.objects.filter(clenstvi__clovek=self))


class Atribut(models.Model):

    """ Vlastnost cloveka,
    dle ktere muze byt specialne kategorizovan """

    nazev = models.CharField(u'Název atributu', max_length=30, unique=True)
    info = models.TextField(u'Info', null=True, blank=True)

    class Meta:
        verbose_name = u'Atribut člověka'
        verbose_name_plural = u'Atributy lidí'

    def __unicode__(self):
        return self.nazev


class Clenstvi(models.Model):

    """ Propojeni cloveka, klubu a sportu,
    mezi clovekem a klubem je vztah m2m """

    clovek = models.ForeignKey(
        'Clovek',
        verbose_name=u'člověk',
        related_name='clenstvi')
    klub = models.ForeignKey(
        'kluby.Klub',
        verbose_name=u'klub',
        related_name='clenstvi')
    sport = models.ForeignKey(
        'zavody.Sport',
        on_delete=models.SET_NULL,
        null=True, blank=True)
    priorita = models.SmallIntegerField(
        u'Priorita', null=True, blank=True,
        help_text=u'určuje prioritu klubů se stejným sportem - větší číslo vyhrává !')

    class Meta:
        verbose_name = u'Členství v klubu'
        verbose_name_plural = u'Členství v klubech'
        ordering = ('clovek', '-sport', '-priorita')
        unique_together = ('clovek', 'klub', 'sport')


    def __unicode__(self):
        return u'{0} - {1}'.format(self.clovek, self.klub)
