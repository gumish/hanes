# Generated by Django 4.0.5 on 2022-07-18 06:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('zavody', '0002_remove_kategorie_atributy'),
        ('pohary', '0002_remove_kategoriepoharu_atributy'),
        ('lide', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clovek',
            name='atributy',
        ),
        migrations.DeleteModel(
            name='Atribut',
        ),
    ]
