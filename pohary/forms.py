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


class PocetZavoduPoharuSportuInline(InlineFormSetFactory):
    model = PocetZavoduPoharuSportu
    fields = "__all__"
    factory_kwargs = {
        "extra": 3,
        "can_delete": True,
    }
