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
            'kluby': forms.Select({'class': 'ui search dropdown', 'multiple': 'multiple'}),
            'rocniky': forms.Select({'class': 'ui search dropdown', 'multiple': 'multiple'}),
            'datum': forms.DateInput({'type': 'date'}),
            'info': forms.Textarea({'rows': 5}),
        }


class PocetZavoduPoharuSportuInline(InlineFormSetFactory):
    model = PocetZavoduPoharuSportu
    fields = "__all__"
    factory_kwargs = {
        "extra": 3,
        "can_delete": True,
    }
