from django import forms
from core.mixins import BootstrapFormMixin
from .models import Invoice, Payment, MaintenanceChargeTemplate


class InvoiceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['flat', 'title', 'amount', 'due_date', 'notes']
        widgets = {'due_date': forms.DateInput(attrs={'type': 'date'})}


class PaymentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method', 'reference_number']


class MaintenanceChargeTemplateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = MaintenanceChargeTemplate
        fields = ['name', 'amount', 'is_active', 'description']
