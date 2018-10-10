# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lide', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Kategorie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazev', models.CharField(max_length=50, verbose_name='N\xe1zev')),
                ('znacka', models.CharField(help_text='zna\u010dka kategorie se pou\u017eije p\u0159i        porovn\xe1v\xe1n\xed s vnucen\xfdmi kategoriemi z\xe1vodn\xedk\u016f <b>u kategori\xed poh\xe1r\u016f</b>', max_length=10, null=True, verbose_name='Zna\u010dka', blank=True)),
                ('pohlavi', models.CharField(blank=True, max_length=1, null=True, verbose_name='Pohlav\xed', choices=[(b'm', 'mu\u017ei'), (b'z', '\u017eeny')])),
                ('vek_od', models.SmallIntegerField(help_text='v\u011bk z\xe1vodn\xedka v\u010detn\u011b', null=True, verbose_name='V\u011bk od', blank=True)),
                ('vek_do', models.SmallIntegerField(help_text='v\u011bk z\xe1vodn\xedka v\u010detn\u011b', null=True, verbose_name='V\u011bk do', blank=True)),
                ('delka_trate', models.CharField(max_length=20, null=True, verbose_name='D\xe9lka trat\u011b', blank=True)),
                ('poradi', models.SmallIntegerField(null=True, verbose_name='Po\u0159ad\xed', blank=True)),
                ('spusteni_stopek', models.TimeField(help_text='st\u0159edoevropsk\xfd \u010das, kdy byli pro kategorii spu\u0161t\u011bny stopky', null=True, verbose_name='\u010cas spu\u0161t\u011bn\xed stopek kategorie', blank=True)),
                ('startovne', models.SmallIntegerField(null=True, verbose_name='Startovn\xe9', blank=True)),
                ('atributy', models.ManyToManyField(to='lide.Atribut', verbose_name='Po\u017eadovan\xe9 atributy \u010dlov\u011bka', blank=True)),
            ],
            options={
                'ordering': ('poradi', 'id'),
                'verbose_name': 'Kategorie',
                'verbose_name_plural': 'Kategorie',
            },
        ),
        migrations.CreateModel(
            name='Rocnik',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazev', models.CharField(help_text='pokud nen\xed n\xe1zev vypln\u011bn, pak se d\u011bd\xed z rodi\u010dovsk\xe9ho z\xe1vodu', max_length=50, null=True, verbose_name='N\xe1zev', blank=True)),
                ('datum', models.DateField(verbose_name='Datum po\u0159\xe1d\xe1n\xed')),
                ('cas', models.TimeField(null=True, verbose_name='\u010cas', blank=True)),
                ('misto', models.CharField(help_text='pokud nen\xed m\xedsto vypln\u011bno, pak se d\u011bd\xed z rodi\u010dovsk\xe9ho z\xe1vodu', max_length=120, null=True, verbose_name='M\xedsto kon\xe1n\xed', blank=True)),
                ('info', models.TextField(null=True, verbose_name='Info', blank=True)),
            ],
            options={
                'ordering': ('-datum',),
                'verbose_name': 'Ro\u010dn\xedk z\xe1vodu',
                'verbose_name_plural': 'Ro\u010dn\xedky zavod\u016f',
            },
        ),
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazev', models.CharField(unique=True, max_length=50, verbose_name='N\xe1zev')),
                ('slug', models.SlugField(editable=False)),
                ('info', models.TextField(null=True, verbose_name='Info', blank=True)),
            ],
            options={
                'verbose_name': 'Sport',
                'verbose_name_plural': 'Sporty',
            },
        ),
        migrations.CreateModel(
            name='Zavod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazev', models.CharField(unique=True, max_length=50, verbose_name='N\xe1zev')),
                ('slug', models.SlugField(unique=True, editable=False)),
                ('korekce_sezony', models.BooleanField(default=False, help_text='zatrhni u podzimn\xedch ly\u017ea\u0159sk\xfdch b\u011bh\u016f pro pou\u017eit\xed kategori\xed zimn\xed sez\xf3ny', verbose_name='Korekce sez\xf3ny')),
                ('misto', models.CharField(max_length=120, null=True, verbose_name='M\xedsto', blank=True)),
                ('info', models.TextField(null=True, verbose_name='Info', blank=True)),
                ('sport', models.ForeignKey(related_name='zavody', verbose_name='sport', to='zavody.Sport')),
            ],
            options={
                'ordering': ('-rocniky__datum', 'sport', 'nazev'),
                'verbose_name': 'Z\xe1vod',
                'verbose_name_plural': 'Z\xe1vody',
            },
        ),
        migrations.AddField(
            model_name='rocnik',
            name='zavod',
            field=models.ForeignKey(related_name='rocniky', verbose_name='z\xe1vod', to='zavody.Zavod'),
        ),
        migrations.AddField(
            model_name='kategorie',
            name='rocnik',
            field=models.ForeignKey(related_name='kategorie', verbose_name='ro\u010dn\xedk', to='zavody.Rocnik'),
        ),
        migrations.AlterUniqueTogether(
            name='rocnik',
            unique_together=set([('zavod', 'datum')]),
        ),
        migrations.AlterUniqueTogether(
            name='kategorie',
            unique_together=set([('rocnik', 'nazev')]),
        ),
    ]
