# coding: utf-8
from django import forms

from .models import Pohar


class PoharCreateForm(forms.ModelForm):
    kopirovat_kategorie = forms.BooleanField(
        label=u'Kopírovat kategorie z prvního závodu?', initial=True, required=False)

    class Meta:
        model = Pohar
        fields = '__all__'
