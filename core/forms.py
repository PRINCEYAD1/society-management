from django import forms
from core.mixins import BootstrapFormMixin
from .models import Society, Building, Flat


class SocietyForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Society
        fields = ['name', 'address', 'registration_number', 'contact_email', 'contact_phone']


class BuildingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Building
        fields = ['society', 'name', 'total_floors']


class FlatForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Flat
        fields = ['building', 'flat_number', 'floor', 'area_sqft', 'ownership_type']
