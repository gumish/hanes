# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pohary', '0002_auto_20170120_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bodovehodnoceni',
            name='hodnoceni',
            field=models.TextField(help_text='form\xe1t:<br>1-50<i>(enter)</i><br>2-47<br>3-44', verbose_name='Hodnocen\xed prvn\xedch pozic'),
        ),
        migrations.AlterField(
            model_name='kategoriepoharu',
            name='znacka',
            field=models.CharField(help_text='zna\u010dka kategorie se pou\u017eije p\u0159i        porovn\xe1v\xe1n\xed s <b>vnucen\xfdmi kategoriemi</b> z\xe1vodn\xedk\u016f', max_length=10, null=True, verbose_name='Zna\u010dka', blank=True),
        ),
    ]
