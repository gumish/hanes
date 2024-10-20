# Generated by Django 4.0.5 on 2024-10-20 06:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kluby', '0003_klub_klub_id_klub_zkratka'),
        ('pohary', '0002_remove_kategoriepoharu_atributy'),
    ]

    operations = [
        migrations.AddField(
            model_name='pohar',
            name='kluby',
            field=models.ManyToManyField(blank=True, help_text='pokud není zadán žádný Klub, pak se použijí všechny', related_name='pohary', to='kluby.klub', verbose_name='Kluby'),
        ),
    ]
