# coding: utf-8
from django.db import models
from django.utils.text import slugify


class Klub(models.Model):
    nazev = models.CharField(u'Název', max_length=50, unique=True)
    slug = models.SlugField(editable=False, unique=True)
    nazev_slug_sorting = models.SlugField(editable=False, unique=False)
    sport = models.ForeignKey(
        'zavody.Sport',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        verbose_name=u'sport',
        related_name='kluby')
    info = models.TextField(u'Info', null=True, blank=True)

    class Meta:
        verbose_name = u'Klub'
        verbose_name_plural = u'Kluby'
        ordering = ('nazev_slug_sorting',)

    def __unicode__(self):
        return self.nazev

    @models.permalink
    def get_absolute_url(self, user=None):
        if user and user.is_active:
            return ('kluby:klub_update', (self.slug,))
        else:
            return ('kluby:klub_detail', (self.slug,))

    def save(self, *args, **kwargs):
        from lide.models import _vytvor_sorting_slug
        self.slug = slugify(self.nazev)
        self.nazev_slug_sorting = _vytvor_sorting_slug(self.nazev)
        super(Klub, self).save(*args, **kwargs)
