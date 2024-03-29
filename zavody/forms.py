
import csv
from django import forms
from django.forms.formsets import BaseFormSet, formset_factory
from django.core.exceptions import ValidationError, MultipleObjectsReturned
from django.db import transaction
from django.forms.models import inlineformset_factory, BaseInlineFormSet

from lide.forms import LideImportCSVForm
from .models import Zavodnik, Zavod, Sport, Rocnik, Kategorie
from .functions import kategorie_import
from zavodnici.custom_fields import CustomTimeField


# FORMS
# -----

class ImportCasuTextForm(forms.Form):
    text =  forms.CharField(
        label='text',
        help_text='''
            příklad:
            03:02.4 (ignorováno)
            01:50.4 (ignorováno)
            --------------------------------- (ignorováno)
            3:  00:09.6   00:02.8
            2:  00:06.7   00:01.9
            1:  00:04.8   00:04.8''',
        required=True,
        widget=forms.Textarea()
    )

    def clean(self):
        """ Zpracuje formular do podoby:
            [{'cilovy_cas':'0:30:00', 'cislo': ''}, ..]
        """
        result = []
        text_list = self.cleaned_data['text'].split('\n')
        text_list.reverse()
        for radek in text_list:
            if radek.startswith('---'):
                break
            radek_list = radek.split()
            result.append({
                'cilovy_cas': radek_list[1],
                'cislo': ''
            })
        return result


class ImportCasuSouborForm(forms.Form):
    soubor = forms.FileField(
        label='soubor *.txt',
        help_text='soubor s výslednými časy z mobilní aplikace',
        required=True,
        widget=forms.FileInput(attrs={'accept': '.txt'}))

    def clean(self):
        """ Zpracuje formular do podoby:
            [{'cilovy_cas':'0:30:00', 'cislo': '12'}, ..]
        """
        result = []
        soubor = self.cleaned_data['soubor']
        csvreader = csv.reader(soubor, delimiter='\t')
        next(csvreader)  # preskoceni prvniho radku
        for radek in csvreader:
            result.append({
                'cilovy_cas': radek[1],
                'cislo': radek[2]
            })
        return result


class ImportCilovehoCasuFormular(forms.Form):
    cislo = forms.IntegerField(label='Startovní číslo', min_value=0)
    cilovy_cas = CustomTimeField(label='Cílový čas', required=True)
    prepsat = forms.BooleanField(required=False, help_text='povolit přepsání již zapsaných časů')

    def clean_cislo(self):
        """
        existuje startovni cislo?
        - ANO: priradi se existujici zavodnik
        - NE: vytvori se docasny zavodnik bez cloveka
        drive se to hodila jako chyba (kod nize)
        """
        cislo = self.cleaned_data['cislo']

        self.zavodnik, created = Zavodnik.objects.get_or_create(
            cislo=cislo, rocnik=self.rocnik)

        return cislo

    def clean(self):
        data = self.cleaned_data
        if self.zavodnik and not self.cleaned_data['prepsat']:
            if self.zavodnik.cilovy_cas:
                raise forms.ValidationError(
                    {'cilovy_cas': '''<u>Závodník má již zadaný čas.</u><br>
                    Pokud ho chceš přepsat, zatrhni políčko vpravo.'''})
            elif self.zavodnik.nedokoncil:
                raise forms.ValidationError(
                    {'cilovy_cas': '''<u>Závodník závod nedokončil!</u><br>
                    Pokud i tak chceš cílový čas zapsat,<br>
                    zatrhni políčko vpravo.'''})
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        if data:
            zavodnik = self.zavodnik
            if data['cilovy_cas']:
                zavodnik.cilovy_cas = data['cilovy_cas']
            zavodnik.save()


class CilovyFormular(forms.Form):
    cislo = forms.IntegerField(label='Startovní číslo', min_value=0)
    cilovy_cas = CustomTimeField(label='Cílový čas', required=False)
    nedokoncil = forms.ChoiceField(
        label='Nedokonončil(a)', required=False,
        choices=((None, '---'),) + Zavodnik.NEDOKONCIL,
        widget=forms.Select(attrs={'tabindex': '-1'}))
    prepsat = forms.BooleanField(
        required=False,
        help_text='povolit přepsání již zapsaných časů',
        widget=forms.CheckboxInput(attrs={'tabindex': '-1'}))

    def clean_cislo(self):
        """
        existuje startovni cislo?
        - ANO: priradi se existujici zavodnik
        - NE: vytvori se docasny zavodnik bez cloveka
        drive se to hodila jako chyba (kod nize)
        """
        cislo = self.cleaned_data['cislo']

        self.zavodnik, created = Zavodnik.objects.get_or_create(
            cislo=cislo, rocnik=self.rocnik)

        return cislo

    def clean_nedokoncil(self):
        nedokoncil = self.cleaned_data['nedokoncil']
        return None if not nedokoncil else nedokoncil

    def clean(self):

        " vzajemna validace mezi policky formulare "

        data = self.cleaned_data
        if not ('cilovy_cas' in data or data['nedokoncil']):
            raise ValidationError({'cilovy_cas': 'Musí být vyplněn buď `cílový čas` nebo `nedokončil`'})
        if hasattr(self, 'zavodnik') and not self.cleaned_data['prepsat']:
            if self.zavodnik.cilovy_cas:
                raise forms.ValidationError(
                    {'cilovy_cas': '''<u>Závodník má již zadaný čas.</u><br>
                    Pokud ho chceš přepsat, zatrhni políčko vpravo.'''})
            elif self.zavodnik.nedokoncil:
                raise forms.ValidationError(
                    {'cilovy_cas': '''<u>Závodník závod nedokončil!</u><br>
                    Pokud i tak chceš cílový čas zapsat,<br>
                    zatrhni políčko vpravo.'''})
        return self.cleaned_data

    def save(self):
        data = self.cleaned_data
        if data:
            zavodnik = self.zavodnik
            if data['cilovy_cas']:
                zavodnik.cilovy_cas = data['cilovy_cas']
            zavodnik.nedokoncil = data['nedokoncil']
            zavodnik.save()
            return zavodnik
        else:
            return None


class ZavodCreateForm(forms.ModelForm):
    sport = forms.CharField(label='Sport')

    class Meta:
        model = Zavod
        fields = ('nazev', 'sport', 'korekce_sezony', 'misto', 'info')

    def clean_sport(self):
        sport, created = Sport.objects.get_or_create(nazev=self.cleaned_data['sport'])
        return sport


class RocnikCreateForm(forms.ModelForm):
    kategorie = forms.FileField(
        label='Import kategorií z *.csv', required=False,
        widget=forms.FileInput(attrs={'accept': '.csv'}),
        help_text='pro nové kategorie nahrát soubor CSV, jinak se budou dědit z předcházejícího ročníku')

    class Meta:
        model = Rocnik
        fields = ('zavod', 'datum', 'cas', 'misto', 'nazev', 'info')

    def clean_kategorie(self):
        soubor = self.cleaned_data['kategorie']
        if soubor:
            kategorie_list, chyby = kategorie_import(soubor)
            if chyby:
                raise ValidationError({
                    'kategorie': chyby[0]
                })
            else:
                return kategorie_list
        else:
            return None

    def save(self, *args, **kwargs):
        rocnik = super(RocnikCreateForm, self).save(*args, **kwargs)
        return (rocnik, self.cleaned_data['kategorie'])


class ImportZavodnikuCSVForm(LideImportCSVForm):
    '''naimportuje zavodniky, treba i kategoriemi'''

    @transaction.atomic
    def save(self, rocnik):
        # ulozi lidi a kluby
        lide = super(ImportZavodnikuCSVForm, self).save()
        zavodnici = []
        for radek in lide:
            clovek, klub, novy_clovek, novy_klub, radek = radek
            try:
                zavodnik, zavodnik_novy = Zavodnik.objects.get_or_create(
                    clovek=clovek,
                    rocnik=rocnik,
                    defaults={
                        'klub': klub,
                        'cislo': radek['cislo']
                        # 'startovni_cas': radek['startovni_cas'],
                        # 'cilovy_cas': radek['cilovy_cas']
                    })
                zavodnici.append(
                    (zavodnik, zavodnik_novy, radek['defaults']))
            except MultipleObjectsReturned as e:
                print((clovek, e))
        return zavodnici


class SloupceVysledkoveListinyForm(forms.Form):
    startovni_cas = forms.BooleanField(required=False, label='startovní čas', initial=False)
    cilovy_cas = forms.BooleanField(required=False, label='cílový čas', initial=False)
    casova_ztrata = forms.BooleanField(required=False, label='časová ztráta', initial=False)
    poradi_na_trati = forms.BooleanField(required=False, label='pořadí na trati', initial=True)


class StartovniCasKategorieForm(forms.ModelForm):
    class Meta:
        model = Kategorie
        fields = ['spusteni_stopek']
        widgets = {
            'spusteni_stopek': forms.TimeInput(
                attrs={'placeholder': 'hh:mm:ss'}
            )
        }


class CisloStartovniCasZavodnikaForm(forms.ModelForm):
    """
    Formular pouzit v startovni_casy.html
    """

    class Meta:
        model = Zavodnik
        fields = ['cislo', 'startovni_cas']

    def has_changed(self):
        """
        Prepsani interni fce rodice.
        Aby se ukladal vzdy, i kdyz se cas nezmeni,
        ale zmeni se kategorie a je nutno prepocitat
        """
        return True


    def clean_cislo(self):
        """
        Vynechani validace cisla, tak aby mohlo byt cislo v zavode klidne i vicekrat
        """
        print('clean_cislo')
        cislo = self.cleaned_data['cislo']
        return cislo

    def clean(self):
        print('CLEAN')


# FORMSETS
# -----
class KontrolaKolonekFormSet(BaseFormSet):
    kontrolovano_list = []
    chybova_hlaska = None

    def clean(self):
        """ kontrola, zda se neopakuji hodnoty v kolonkach
            - kontrolovano_list: seznam nazvu kolonek, ktere se maji kontrolovat
        """
        if any(self.errors):
            return
        list_listu_hodnot = []  # listu listu hodnot formularu
        for form in self.forms:
            hodnoty = []  # list hodnot v jednom formu
            for kolonka in self.kontrolovano_list:
                value = form.cleaned_data.get(kolonka, '')
                if isinstance(value, int):
                    value = str(value)
                elif not value:
                    value = ''
                hodnoty.append(value)
            if all(hodnoty):
                if hodnoty in list_listu_hodnot:
                    raise forms.ValidationError(self.chybova_hlaska.format(*hodnoty))
                list_listu_hodnot.append(hodnoty)


class KontrolaCiselFormSet(KontrolaKolonekFormSet):
    kontrolovano_list = ('cislo',)
    chybova_hlaska = 'Číslo {0} ve formuláři musí být pouze jednou!'


class KontrolaLidiFormSet(KontrolaKolonekFormSet):
    kontrolovano_list = ('prijmeni', 'jmeno', 'narozen', 'cislo')
    chybova_hlaska = '{0} {1} ({2}) s číslem {3} může být ve formuláři pouze jednou!'


class PridaniZavodnikuFormSet(KontrolaLidiFormSet):
    pass


class KontrolaCiselInlineFormSet(BaseInlineFormSet):

    def full_clean(self):
        return
#     pass
    # def is_valid(self):
    #     """
    #     zkontroluje zda-li nekde v jinych kategoriich nejsou stejna cisla zavodniku
    #     """
    #     form_valid = super(KontrolaCiselInlineFormSet, self).is_valid()
    #     print(form_valid)
    #     if form_valid:
    #         kategorie = self.instance
    #         print(self.forms[0].cleaned_data)
    #         cisla = [form.cleaned_data.get('cislo', None) for form in self.forms]
    #         is_dupl_cislo = Zavodnik.objects.exclude(kategorie_temp=kategorie).filter(cislo__in=cisla).exists()
    #         print(cisla, is_dupl_cislo)
    #         if is_dupl_cislo:
    #             raise forms.ValidationError(u"Chyba. Duplikatni cislo.")
    #     return False


# Formset zavodniku kategorie pri zadavani startovnich casu
ZavodniciKategorieFormSet = inlineformset_factory(
    Kategorie,
    Zavodnik,
    form=CisloStartovniCasZavodnikaForm,
    formset=KontrolaCiselInlineFormSet,
    fk_name='kategorie_temp',
    can_delete=False,
    extra=0
)

ImportyCilovehoCasuFormSet = formset_factory(
    ImportCilovehoCasuFormular,
    formset=KontrolaCiselFormSet,
    extra=3)
