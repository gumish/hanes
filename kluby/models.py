from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Klub(models.Model):
    nazev = models.CharField('Název', max_length=50, unique=True)
    zkratka = models.CharField('Zkratka', max_length=20, null=True, blank=True, default='')
    klub_id = models.PositiveSmallIntegerField('Klubové ID', null=True, blank=True)
    slug = models.SlugField(editable=False, unique=True)
    nazev_slug_sorting = models.SlugField(editable=False, unique=False)
    sport = models.ForeignKey(
        'zavody.Sport',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name='sport',
        related_name='kluby')
    info = models.TextField('Info', null=True, blank=True)

    class Meta:
        verbose_name = 'Klub'
        verbose_name_plural = 'Kluby'
        ordering = ('nazev_slug_sorting',)

    def __str__(self):
        return self.nazev

    def get_absolute_url(self, user=None):
        if user and user.is_active:
            return reverse('kluby:klub_update', args=(self.slug,))
        else:
            return reverse('kluby:klub_detail',args=(self.slug,))

    def save(self, *args, **kwargs):
        """ Pri ukladani nastavi slug a nazev_slug_sorting
        """
        from lide.models import _get_sorting_slug
        self.nazev = self.nazev.strip()
        self.slug = slugify(self.nazev) or '-'
        self.nazev_slug_sorting = _get_sorting_slug(self.nazev)
        super().save(*args, **kwargs)
