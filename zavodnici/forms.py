from datetime import date

from django import forms
from django.utils.text import slugify

from hanes.mixins import disable_fields
from kluby.models import Klub
from lide.models import POHLAVI, Clovek, Stat
from zavody.models import Kategorie

from .custom_fields import CustomTimeField
from .models import Zavodnik


# FORMS
class ZavodnikPridaniForm(forms.ModelForm):
    prijmeni = forms.CharField(label='Příjmení')
    jmeno = forms.CharField(label='Jméno')
    pohlavi = forms.ChoiceField(label='Pohlaví', choices=POHLAVI, required=False)
    narozen = forms.IntegerField(label='Narozen(a)', min_value=date.today().year - 120, max_value=date.today().year)
    stat = forms.ModelChoiceField(
        label='Stát',
        queryset=Stat.objects.all(),
        required=False, initial=Stat.objects.first()
    )
    klub_nazev = forms.CharField(label='Klub', required=False)

    class Meta:
        model = Zavodnik
        fields = (
            'cislo',
            'prijmeni',
            'jmeno',
            'pohlavi',
            'narozen',
            'stat',
            'klub_nazev',
            'kategorie')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['stat'].queryset = Stat.objects.order_by('poradi', 'nazev')
        if self.instance and getattr(self.instance, 'clovek_id', None):
            self.initial['stat'] = self.instance.clovek.stat_id

    def clean(self):
        'z důvodu validace se `Clovek` vytvari uz v `clean` funkci'
        data = super().clean()
        stat = data.get('stat')
        if self.instance.clovek:
            Clovek.objects.filter(id=self.instance.clovek.id).update(
                prijmeni=data['prijmeni'],
                jmeno=data['jmeno'],
                narozen=data['narozen'],
                pohlavi=data['pohlavi'],
                stat=stat,
            )
            self.instance.clovek.stat = stat
        else:
            clovek, _ = Clovek.objects.get_or_create(
                prijmeni=data['prijmeni'],
                jmeno=data['jmeno'],
                narozen=data['narozen'],
                defaults={'pohlavi': data['pohlavi'], 'stat': stat}
            )
            self.instance.clovek = clovek
        return data

    def full_clean(self):
        '''prepsani defaultni funkce
         - pokud nejsou splneny podminky pro policka,
         pak preskoc dalsi kontrolu'''
        # puvodni kod
        from django.forms.utils import ErrorDict
        self._errors = ErrorDict()
        if not self.is_bound:
            return
        self.cleaned_data = {}
        if self.empty_permitted and not self.has_changed():
            return

        self._clean_fields()
        # pokud jsou chybi z fields, ukonci kontrolu
        if not self._errors:
            self._clean_form()
            self._post_clean()

    def add_error(self, field, error):
        "prepsani defaultni funkce `add_error`, aby prejmenovala chybu `clovek` na `prijmeni`"
        try:
            if 'clovek' in error.error_dict:
                error.error_dict['prijmeni'] = error.error_dict.pop('clovek')
        except Exception:
            pass
        super().add_error(field, error)

    def save(self):
        """
        - pokud existuje uz zavodnik se stejnym cislem, pak jenom upravi kategorii na novou z formulare
        - # pokud existuje uz zavodnik, pak jenom upravi jeho cislo, klub, kategorii (upraveno 2023-05-22 na prani)
        - automaticky zarazuje cloveka do klubu
        - pokud neexistuje vytvari nove clenstvi
        - dovyplnuje `zavodnika` a uklada ho
        """
        data = self.cleaned_data

        # existuje uz obdobny zavodnik?
        existujici = (
            Zavodnik.objects
            .filter(clovek=self.instance.clovek, rocnik=self.instance.rocnik, cislo=self.instance.cislo)
            .exclude(id=self.instance.id)
            .first()
        )
        if existujici:
            self.instance = existujici
            for attr in ('kategorie',):
                if data.get('attr'):
                    setattr(self.instance, attr, data[attr])

        # pokud je vyplnena kategorie, pak ho rovnou i prirad
        if self.instance.kategorie:
            self.instance.kategorie_temp = self.instance.kategorie

        # vytvor klub pokud neexistuje a prirad ho zavodnikovi
        if data.get('klub_nazev'):
            slug = slugify(data['klub_nazev'])
            klub, _ = Klub.objects.get_or_create(
                slug=slug,
                defaults={
                    'nazev': data['klub_nazev'].strip(),
                    'sport': self.instance.rocnik.zavod.sport,
                })
            self.instance.klub = klub

        self.instance.save()


class ZavodnikEditaceForm(ZavodnikPridaniForm):
    startovni_cas = CustomTimeField(label='Startovní čas')
    cilovy_cas = CustomTimeField(label='Cílový čas')

    class Meta:
        model = Zavodnik
        fields = (
            'prijmeni',
            'jmeno',
            'pohlavi',
            'narozen',
            'stat',
            'cislo',
            'klub_nazev',
            'kategorie',
            'kategorie_temp',
            'startovni_cas',
            'cilovy_cas',
            'nedokoncil',
            'odstartoval',
            'nedokoncil')

    def __init__(self, *args, **kwargs):
        "editace závodníka > dle `instance` vyplni pole `prijemni, jmeno, atd.`"
        super().__init__(*args, **kwargs)
        if self.instance:
            zavodnik = self.instance
            self.rocnik = zavodnik.rocnik
            if zavodnik.clovek:
                self.initial['prijmeni'] = zavodnik.clovek.prijmeni
                self.initial['jmeno'] = zavodnik.clovek.jmeno
                self.initial['narozen'] = zavodnik.clovek.narozen
                self.initial['pohlavi'] = zavodnik.clovek.pohlavi
                self.initial['stat'] = zavodnik.clovek.stat_id
            self.initial['klub_nazev'] = zavodnik.klub
            self.fields['kategorie'].queryset = Kategorie.objects.filter(rocnik=self.rocnik)
        disable_fields(self, ['kategorie_temp'])


class ZavodnikForm(forms.ModelForm):
    startovni_cas = CustomTimeField()
    cilovy_cas = CustomTimeField()

    class Meta:
        model = Zavodnik
        fields = ('cislo', 'startovni_cas', 'cilovy_cas', 'nedokoncil')

    def add_error(self, field, error):
        "prepsani defaultni funkce `add_error`, aby prejmenovala chybu `clovek` na `prijmeni`"
        try:
            if 'clovek' in error.error_dict:
                del error.error_dict['clovek']
        except:
            pass
        super().add_error(field, error)


class StarterZavodnikForm(forms.ModelForm):
    # startovni_cas = CustomTimeField()

    class Meta:
        model = Zavodnik
        fields = ('odstartoval',)
        widgets = {'odstartoval': forms.HiddenInput()}

    def save(self, commit=True):
        zavodnik = super().save(commit=False)
        zavodnik.save(nekontroluj=True)
        return zavodnik
