# coding: utf-8
from django import forms
from django.db import transaction
from django.utils.text import slugify

from .models import Clovek, Clenstvi
from kluby.models import Klub
from .functions import clean_lide_import_csv
from zavody.models import Zavodnik


class ClovekUpdateForm(forms.ModelForm):
    smazat = forms.BooleanField(
        label=u'Smazat člověka',
        required=False)
    presunout_vysledky = forms.ModelChoiceField(
        label=u'Výsledky přesunout na jiného člověka',
        required=False,
        queryset=Clovek.objects.all(),
        help_text=u'Výsledky lze přesunout na jiného člověka i bez smazání původního člověka.',
        widget=forms.Select(attrs={'class': 'dropdown search'}))

    class Meta:
        model = Clovek
        fields = ('prijmeni', 'jmeno', 'pohlavi', 'narozen', 'atributy')
        widgets = {
            'atributy': forms.SelectMultiple(attrs={'class': 'dropdown'})
        }

    def __init__(self, *arg, **kwargs):
        super(ClovekUpdateForm, self).__init__(*arg, **kwargs)
        self.fields['presunout_vysledky'].queryset = Clovek.objects.exclude(pk=self.instance.pk)

    def save(self, *args, **kwargs):
        '''-prevadi vysledky na noveho cloveka
        - maze aktualniho cloveka
        - vytvari zpravy pro `messages`'''
        data = self.cleaned_data
        zpravy = []
        clovek = None
        if data['presunout_vysledky']:
            clovek = data['presunout_vysledky']
            Zavodnik.objects.filter(clovek=self.instance).update(clovek=clovek)
            zpravy.append(
                u"Výsledky přesunuty z člověka '{0}'' na '{1}'".format(self.instance, clovek))

        if data['smazat']:
            zpravy.append(u"Člověk '{0}' smazán".format(self.instance))
            self.instance.delete()
            smazan = True
        else:
            clovek = super(ClovekUpdateForm, self).save(*args, **kwargs)
            zpravy.append(u'změny v člověku uloženy')
            smazan = False

        return (clovek, zpravy, smazan)


class CSVsouborFormular(forms.Form):
    soubor = forms.FileField(
        label=u'soubor *.csv',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.csv'}))


class LideImportCSVForm(forms.Form):
    soubor = forms.FileField(
        label=u'soubor *.csv',
        help_text=u'csv soubor seznamu lidí (může být i s hlavičkou) v pořadí:\
        příjmení, jméno, pohlaví, rok narození, klub',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.csv'}))

    def clean_soubor(self):
        radky, chyby = clean_lide_import_csv(self.cleaned_data['soubor'])
        if chyby:
            raise forms.ValidationError(chyby)
        else:
            return radky

    @transaction.atomic
    def save(self):
        lide = []
        radky = self.cleaned_data['soubor']
        for radek in radky:
            clovek, novy_clovek = Clovek.objects.get_or_create(
                slug__startswith=radek['slug'],
                defaults=radek['defaults'])

            if radek['klub']:
                klub, novy_klub = Klub.objects.get_or_create(
                    slug=slugify(radek['klub']),
                    defaults={'nazev': radek['klub']})

                if not Clenstvi.objects.filter(clovek=clovek, klub=klub).exists():
                    Clenstvi.objects.create(
                        clovek=clovek,
                        klub=klub)
            else:
                klub = None
                novy_klub = None
            lide.append(
                (clovek, klub, novy_clovek, novy_klub, radek))
        return lide
