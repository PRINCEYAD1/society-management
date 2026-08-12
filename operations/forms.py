from django import forms
from .models import Vehicle, Parcel, VendorAMC, Expense, MoveRequest


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


class VehicleForm(StyledModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        widgets = {'photo': forms.FileInput(attrs={'accept': 'image/*'})}


class ParcelForm(StyledModelForm):
    class Meta:
        model = Parcel
        exclude = ['received_at', 'collected_at', 'received_by']
        widgets = {'photo': forms.FileInput(attrs={'accept': 'image/*'})}


class VendorAMCForm(StyledModelForm):
    class Meta:
        model = VendorAMC
        fields = '__all__'
        widgets = {'start_date': forms.DateInput(attrs={'type':'date'}), 'renewal_date': forms.DateInput(attrs={'type':'date'})}


class ExpenseForm(StyledModelForm):
    class Meta:
        model = Expense
        exclude = ['created_by']
        widgets = {'expense_date': forms.DateInput(attrs={'type':'date'}), 'receipt': forms.FileInput(attrs={'accept':'image/*'})}


class MoveRequestForm(StyledModelForm):
    class Meta:
        model = MoveRequest
        exclude = ['requested_by', 'created_at']
        widgets = {'requested_date': forms.DateInput(attrs={'type':'date'})}
