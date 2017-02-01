# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pohary', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='kategoriepoharu',
            name='bod_hodnoceni',
            field=models.ForeignKey(related_name='kategorie', blank=True, to='pohary.BodoveHodnoceni', help_text='bodov\xe1 tabulka pro kategorii poh\xe1ru,<br>        p\u0159i pr\xe1zdn\xe9 kolonce bude pou\u017eita tabulka z poh\xe1ru', null=True, verbose_name='Bodov\xe9 hodnocen\xed'),
        ),
        migrations.AddField(
            model_name='pohar',
            name='bod_hodnoceni',
            field=models.ForeignKey(related_name='pohary', blank=True, to='pohary.BodoveHodnoceni', help_text='bodov\xe1 tabulka pro poh\xe1r,<br>        bude pou\u017eita v p\u0159\xedpad\u011b nespecifikovan\xe9 tabulky u kategorie,<br>        v p\u0159\xedpad\u011b pr\xe1zdn\xe9ho kolonky se boduje postupn\u011b odzadu', null=True, verbose_name='Bodov\xe9 hodnocen\xed'),
        ),
    ]
