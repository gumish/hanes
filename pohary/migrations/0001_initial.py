# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zavody', '__first__'),
        ('lide', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BodoveHodnoceni',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazev', models.CharField(max_length=50, verbose_name='N\xe1zev')),
                ('hodnoceni', models.TextField(help_text='form\xe1t:\n1-50\n2-47\n3-44', verbose_name='Hodnocen\xed prvn\xedch pozic')),
                ('info', models.TextField(null=True, verbose_name='Informace', blank=True)),
            ],
            options={
                'verbose_name': 'Bodov\xe9 hodnocen\xed pozic',
                'verbose_name_plural': 'Bodov\xe1 hodnocen\xed pozic',
            },
        ),
        migrations.CreateModel(
            name='KategoriePoharu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazev', models.CharField(max_length=50, verbose_name='N\xe1zev')),
                ('znacka', models.CharField(max_length=10, null=True, verbose_name='Zna\u010dka', blank=True)),
                ('pohlavi', models.CharField(blank=True, max_length=1, null=True, verbose_name='Pohlav\xed', choices=[(b'm', 'mu\u017ei'), (b'z', '\u017eeny')])),
                ('vek_od', models.SmallIntegerField(help_text='v\u011bk z\xe1vodn\xedka v\u010detn\u011b', null=True, verbose_name='V\u011bk od', blank=True)),
                ('vek_do', models.SmallIntegerField(help_text='v\u011bk z\xe1vodn\xedka v\u010detn\u011b', null=True, verbose_name='V\u011bk do', blank=True)),
                ('poradi', models.SmallIntegerField(null=True, verbose_name='Po\u0159ad\xed', blank=True)),
                ('zavodu', models.SmallIntegerField(help_text='po\u010det nejlep\u0161\xedch z\xe1vod\u016f je\u017e budou zapo\u010d\xedtany,        <br>p\u0159i pr\xe1zdn\xe9 kolonce bude pou\u017eita hodnota poh\xe1ru', null=True, verbose_name='Po\u010det nejlep\u0161\xedch v\xfdsledk\u016f', blank=True)),
                ('atributy', models.ManyToManyField(to='lide.Atribut', verbose_name='Po\u017eadovan\xe9 atributy \u010dlov\u011bka', blank=True)),
            ],
            options={
                'ordering': ('poradi', 'id'),
                'verbose_name': 'Kategorie poh\xe1ru',
                'verbose_name_plural': 'Kategorie poh\xe1r\u016f',
            },
        ),
        migrations.CreateModel(
            name='Pohar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nazev', models.CharField(max_length=50, verbose_name='N\xe1zev')),
                ('datum', models.DateField(verbose_name='Datum po\u0159\xe1d\xe1n\xed')),
                ('slug', models.SlugField(unique=True, editable=False)),
                ('info', models.TextField(null=True, verbose_name='Info', blank=True)),
                ('zavodu', models.SmallIntegerField(help_text='po\u010det nejlep\u0161\xedch z\xe1vod\u016f je\u017e budou zapo\u010d\xedtany,<br>        p\u0159i pr\xe1zdn\xe9 kolonce budou pou\u017eity v\u0161echny z\xe1vody', null=True, verbose_name='Po\u010det nejlep\u0161\xedch v\xfdsledk\u016f', blank=True)),
                ('rocniky', models.ManyToManyField(related_name='pohary', verbose_name='Ro\u010dn\xedky', to='zavody.Rocnik')),
            ],
            options={
                'ordering': ('-datum',),
                'verbose_name': 'Poh\xe1r',
                'verbose_name_plural': 'Poh\xe1ry',
            },
        ),
        migrations.AddField(
            model_name='kategoriepoharu',
            name='pohar',
            field=models.ForeignKey(related_name='kategorie_poharu', verbose_name='poh\xe1r', to='pohary.Pohar'),
        ),
        migrations.AlterUniqueTogether(
            name='pohar',
            unique_together=set([('nazev', 'datum')]),
        ),
        migrations.AlterUniqueTogether(
            name='kategoriepoharu',
            unique_together=set([('pohar', 'nazev')]),
        ),
    ]
