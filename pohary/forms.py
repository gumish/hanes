from django import forms
from extra_views import InlineFormSetFactory

from .models import Pohar, PocetZavoduPoharuSportu


class PoharCreateForm(forms.ModelForm):
    kopirovat_kategorie = forms.BooleanField(
        label="Kopírovat kategorie z prvního závodu?", initial=True, required=False
    )

    class Meta:
        model = Pohar
        fields = "__all__"
        widgets = {
            'kluby': forms.SelectMultiple({'class': 'ui search dropdown', 'multiple': 'multiple'}),
            'rocniky': forms.SelectMultiple({'class': 'ui search dropdown', 'multiple': 'multiple'}),
            'info': forms.Textarea({'rows': 5}),
        }


class PocetZavoduPoharuSportuInline(InlineFormSetFactory):
    model = PocetZavoduPoharuSportu
    fields = "__all__"
    factory_kwargs = {
        "extra": 3,
        "can_delete": True,
    }
