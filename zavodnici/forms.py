# coding: utf-8
from django import forms


from .models import Zavodnik
from zavody.models import Kategorie
from kluby.models import Klub
from lide.models import POHLAVI, Clovek
from .custom_fields import CustomTimeField
from django.utils.text import slugify


# FORMS
class ZavodnikPridaniForm(forms.ModelForm):
    prijmeni = forms.CharField(label=u'Příjmení')
    jmeno = forms.CharField(label=u'Jméno')
    pohlavi = forms.ChoiceField(label=u'Pohlaví', choices=POHLAVI, required=False)
    narozen = forms.IntegerField(label=u'Narozen(a)', min_value=1920, max_value=2020)
    klub_nazev = forms.CharField(label=u'Klub', required=False)

    class Meta:
        model = Zavodnik
        fields = (
            'cislo',
            'prijmeni',
            'jmeno',
            'pohlavi',
            'narozen',
            'klub_nazev',
            'kategorie')

    def clean(self):
        'z důvodu validace se `Clovek` vytvari uz v `clean` funkci'
        data = super(ZavodnikPridaniForm, self).clean()
        clovek, created = Clovek.objects.get_or_create(
            prijmeni=data['prijmeni'],
            jmeno=data['jmeno'],
            narozen=data['narozen'],
            defaults={'pohlavi': data['pohlavi']}
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
        except:
            pass
        super(ZavodnikPridaniForm, self).add_error(field, error)

    def save(self):
        """- automaticky zarazuje cloveka do klubu - pokud neexistuje vytvari nove clenstvi
        - dovyplnuje `zavodnika` a uklada ho
        """
        data = self.cleaned_data
        if data:
            if data['klub_nazev']:
                klub, created = Klub.objects.get_or_create(
                    slug=slugify(data['klub_nazev']),
                    defaults={
                        'sport': self.instance.rocnik.zavod.sport,
                        'nazev': data['klub_nazev']
                    })
                self.instance.klub = klub

            self.instance.kategorie_temp = self.instance.kategorie
            self.instance.save()


class ZavodnikEditaceForm(ZavodnikPridaniForm):
    startovni_cas = CustomTimeField(label=u'Startovní čas')
    cilovy_cas = CustomTimeField(label=u'Cílový čas')

    class Meta:
        model = Zavodnik
        fields = (
            'prijmeni',
            'jmeno',
            'pohlavi',
            'narozen',
            'cislo',
            'klub_nazev',
            'kategorie',
            'startovni_cas',
            'cilovy_cas',
            'nedokoncil',
            'odstartoval',
            'nedokoncil')

    def __init__(self, *args, **kwargs):
        "editace závodníka > dle `instance` vyplni pole `prijemni, jmeno, atd.`"
        super(ZavodnikPridaniForm, self).__init__(*args, **kwargs)
        if self.instance:
            zavodnik = self.instance
            self.rocnik = zavodnik.rocnik
            if zavodnik.clovek:
                self.initial['prijmeni'] = zavodnik.clovek.prijmeni
                self.initial['jmeno'] = zavodnik.clovek.jmeno
                self.initial['narozen'] = zavodnik.clovek.narozen
                self.initial['pohlavi'] = zavodnik.clovek.pohlavi
            self.initial['klub_nazev'] = zavodnik.klub
            self.initial['kategorie'] = zavodnik.kategorie_temp
            self.fields['kategorie'].queryset = Kategorie.objects.filter(rocnik=self.rocnik)


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
        super(ZavodnikForm, self).add_error(field, error)


class StarterZavodnikForm(forms.ModelForm):
    # startovni_cas = CustomTimeField()

    class Meta:
        model = Zavodnik
        fields = ('odstartoval',)
        widgets = {
            'odstartoval': forms.HiddenInput()
        }

    def save(self, commit=True):
        zavodnik = super(StarterZavodnikForm, self).save(commit=False)
        zavodnik.save(nekontroluj=True)
        return zavodnik
