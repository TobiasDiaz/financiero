# coding: utf-8
from django import forms
from django.core.exceptions import ValidationError

from models import producto









class ProductoForm(forms.ModelForm):
    class Meta:
        model = producto

        fields=['nombre', 'ordenDeFabricacion', 'nuneroArticulos',]