from django import forms
from core.mixins import BootstrapFormMixin
from .models import Visitor


class VisitorForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ['name', 'phone_number', 'purpose', 'visiting_flat', 'vehicle_number', 'photo']
