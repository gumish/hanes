
from django import forms

from .models import Klub
from lide.models import Clenstvi
from zavody.models import Zavodnik
from django.utils.text import slugify


class KlubUpdateForm(forms.ModelForm):
    smazat = forms.BooleanField(
        label='Smazat klub',
        required=False)
    presunout_do = forms.CharField(
        label='Členy po smazání přesunout do',
        required=False)

    class Meta:
        model = Klub
        fields = ('nazev', 'sport', 'info')

    def save(self, *args, **kwargs):
        '''-prevadi cleny a zavodniky do novych klubu
        - maze aktualni klubu
        - vytvari zpravy pro `messages`'''

        data = self.cleaned_data
        klub = None
        zpravy = []
        if data['presunout_do']:
            klub = Klub.objects.get_or_create(
                slug=slugify(data['presunout_do']),
                defaults={'nazev': data['presunout_do']}
            )[0]
            Clenstvi.objects.filter(klub=self.instance).update(klub=klub)
            Zavodnik.objects.filter(klub=self.instance).update(klub=klub)
            zpravy.append(
                "členové a závodnici přesunuti z klubu '{0}'' do klubu '{1}'".format(self.instance, klub))

        if data['smazat']:
            zpravy.append("klub '{0}' smazán".format(self.instance))
            self.instance.delete()
        else:
            klub = super(KlubUpdateForm, self).save(*args, **kwargs)
            zpravy.append('změny v klubu uloženy')
        return (klub, zpravy)
