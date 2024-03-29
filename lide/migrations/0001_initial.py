# Generated by Django 4.0.5 on 2022-06-24 08:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('kluby', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Atribut',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nazev', models.CharField(max_length=30, unique=True, verbose_name='Název atributu')),
                ('info', models.TextField(blank=True, null=True, verbose_name='Info')),
            ],
            options={
                'verbose_name': 'Atribut člověka',
                'verbose_name_plural': 'Atributy lidí',
            },
        ),
        migrations.CreateModel(
            name='Clovek',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jmeno', models.CharField(max_length=20, verbose_name='Křestní jméno')),
                ('prijmeni', models.CharField(max_length=30, verbose_name='Příjmení')),
                ('pohlavi', models.CharField(blank=True, choices=[('', '---'), ('m', 'muž'), ('z', 'žena')], max_length=1, null=True, verbose_name='Pohlaví')),
                ('narozen', models.PositiveSmallIntegerField(verbose_name='Narozen(a)')),
                ('jmeno_slug', models.SlugField(blank=True, editable=False)),
                ('prijmeni_slug', models.SlugField(blank=True, editable=False)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('prijmeni_slug_sorting', models.SlugField(editable=False)),
                ('atributy', models.ManyToManyField(blank=True, to='lide.atribut', verbose_name='Atributy člověka')),
            ],
            options={
                'verbose_name': 'Člověk',
                'verbose_name_plural': 'Lidé',
                'ordering': ('prijmeni_slug_sorting', 'jmeno_slug'),
            },
        ),
        migrations.CreateModel(
            name='Clenstvi',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priorita', models.SmallIntegerField(blank=True, help_text='určuje prioritu klubů se stejným sportem - větší číslo vyhrává !', null=True, verbose_name='Priorita')),
                ('clovek', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clenstvi', to='lide.clovek', verbose_name='člověk')),
                ('klub', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='clenstvi', to='kluby.klub', verbose_name='klub')),
            ],
            options={
                'verbose_name': 'Členství v klubu',
                'verbose_name_plural': 'Členství v klubech',
                'ordering': ('clovek', '-sport', '-priorita'),
            },
        ),
    ]
