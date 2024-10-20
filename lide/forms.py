
from django import forms
from django.core.exceptions import MultipleObjectsReturned
from django.db import transaction
from django.db.models import Q, Count

from .models import Clovek, Clenstvi
from kluby.models import Klub
from .functions import zavodnici_import_clean_csv
from zavody.models import Zavodnik


class ClovekUpdateForm(forms.ModelForm):
    smazat = forms.BooleanField(
        label='Smazat člověka',
        required=False)
    presunout_vysledky = forms.ModelChoiceField(
        label='Výsledky přesunout na jiného člověka',
        required=False,
        queryset=Clovek.objects.all(),
        help_text='Výsledky lze přesunout na jiného člověka i bez smazání původního člověka.',
        widget=forms.Select(attrs={'class': 'dropdown search'}))

    class Meta:
        model = Clovek
        fields = ('prijmeni', 'jmeno', 'pohlavi', 'narozen')


    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
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
                "Výsledky přesunuty z člověka '{0}'' na '{1}'".format(self.instance, clovek))

        if data['smazat']:
            zpravy.append("Člověk '{0}' smazán".format(self.instance))
            self.instance.delete()
            smazan = True
        else:
            clovek = super().save(*args, **kwargs)
            zpravy.append('změny v člověku uloženy')
            smazan = False

        return (clovek, zpravy, smazan)


class CSVsouborFormular(forms.Form):
    soubor = forms.FileField(
        label='soubor *.csv',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.csv'}))


class LideImportCSVForm(forms.Form):
    soubor = forms.FileField(
        label='soubor *.csv',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.csv'}))

    def clean_soubor(self):
        radky, chyby = zavodnici_import_clean_csv(self.cleaned_data['soubor'])
        if chyby:
            raise forms.ValidationError(chyby)
        else:
            return radky

    @transaction.atomic
    def save(self):
        lide = []
        radky = self.cleaned_data['soubor']
        for radek in radky:
            try:
                clovek, novy_clovek = Clovek.objects.get_or_create(
                    slug__startswith=radek['slug'],
                    defaults=radek['defaults'])
            except MultipleObjectsReturned:
                # v případě nalezení vícero Človků, přiřadí vybere Člověk s větším počtem účasti v Ročník
                clovek = (
                    Clovek.objects
                    .filter(slug__startswith=radek['slug'])
                    .annotate(pocet_zavodu=Count('zavodnici'))
                    .order_by('-pocet_zavodu').first())
                novy_clovek = False

            if any([radek['klub_nazev'], radek['klub_zkratka'], radek['klub_id']]):

                # pokusi se najit klub dle nenulovych hodnot: klub_nazev, klub_zkratka, klub_id
                klub = Klub.objects.filter(
                    Q(nazev=radek['klub_nazev']) if radek['klub_nazev'] else Q() |
                    Q(zkratka=radek['klub_zkratka']) if radek['klub_zkratka'] else Q() |
                    Q(klub_id=radek['klub_id']) if radek['klub_id'] else Q()
                ).first()
                novy_klub = False

                # pokud nenajde, pokusi se Klub vytvorit
                if not klub:
                    klub = Klub.objects.create(
                        # do nazev dosadi prvni nenulovou hodnotu z klub_nazev, klub_zkratka, klub_id
                        nazev=radek['klub_nazev'] or radek['klub_zkratka'] or radek['klub_id'],
                        zkratka=radek['klub_zkratka'],
                        klub_id=radek['klub_id'] or None)
                    novy_klub = True

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
