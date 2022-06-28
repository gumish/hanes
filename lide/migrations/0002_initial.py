# Generated by Django 4.0.5 on 2022-06-24 08:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('zavody', '0001_initial'),
        ('lide', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='clenstvi',
            name='sport',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='zavody.sport'),
        ),
        migrations.AlterUniqueTogether(
            name='clovek',
            unique_together={('jmeno', 'prijmeni', 'narozen')},
        ),
        migrations.AlterUniqueTogether(
            name='clenstvi',
            unique_together={('clovek', 'klub', 'sport')},
        ),
    ]
