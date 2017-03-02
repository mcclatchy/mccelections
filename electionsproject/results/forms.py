from dal import autocomplete
from django import forms
from .models import *


class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = ('__all__')
        widgets = {
            'race': autocomplete.ModelSelect2(url='race-autocomplete')
        }