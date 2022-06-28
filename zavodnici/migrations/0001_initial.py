# Generated by Django 4.0.5 on 2022-06-24 08:08

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('lide', '0002_initial'),
        ('zavody', '0001_initial'),
        ('kluby', '0002_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Zavodnik',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cislo', models.CharField(blank=True, help_text='číslo je unikátní pro daný ročník - hlídáno', max_length=10, null=True, verbose_name='Startovní číslo')),
                ('startovni_cas', models.TimeField(blank=True, help_text='pokud je zadán, pak se výsledný čas počítá z rozdílu časů start-cíl', null=True, verbose_name='Startovní čas')),
                ('cilovy_cas', models.TimeField(blank=True, help_text='pokud není zadán `startovní čas`, pak se jedná o výsledný čas závodu', null=True, verbose_name='Cílový čas')),
                ('vysledny_cas', models.DurationField(blank=True, editable=False, null=True, verbose_name='Výsledný čas')),
                ('nedokoncil', models.CharField(blank=True, choices=[('DNS', 'DNS'), ('DNF', 'DNF'), ('DSQ', 'DSQ'), ('DNP', 'DNP')], max_length=10, null=True, verbose_name='Nedokončil')),
                ('odstartoval', models.BooleanField(default=None, help_text='pouze informační hodnota od startéra, že závodník opravdu odstartoval', null=True, verbose_name='Odstartoval')),
                ('info', models.CharField(blank=True, max_length=256, null=True, verbose_name='Info')),
                ('clovek', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='zavodnici', to='lide.clovek', verbose_name='člověk')),
                ('kategorie', models.ForeignKey(blank=True, help_text='vnucená kategorie, která ruší automatické přiřazení', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zavodnici', to='zavody.kategorie', verbose_name='kategorie natvrdo')),
                ('kategorie_temp', models.ForeignKey(blank=True, help_text='dočasná kategorie systému', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zavodnici_temp', to='zavody.kategorie', verbose_name='kategorie dočasná')),
                ('klub', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='zavodnici', to='kluby.klub', verbose_name='klub')),
                ('rocnik', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='zavodnici', to='zavody.rocnik', verbose_name='ročník závodu')),
            ],
            options={
                'verbose_name': 'Závodník',
                'verbose_name_plural': 'Závodníci',
                'ordering': ('rocnik', 'vysledny_cas', django.db.models.expressions.OrderBy(django.db.models.expressions.F('startovni_cas'), nulls_last=True), 'cislo'),
            },
        ),
    ]
