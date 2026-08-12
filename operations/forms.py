from django import forms
from .models import (Vehicle, Parcel, VendorAMC, Expense, MoveRequest, DomesticWorker,
                     CertificateRequest, SocietyMeeting, Poll, SocietyAsset,
                     EmergencyContact, LostFoundItem, SocietyEvent)


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            else:
                field.widget.attrs['class'] = 'form-control'


def image_widget(camera=False):
    attrs = {'accept': 'image/*'}
    if camera:
        attrs['capture'] = 'environment'
    return forms.FileInput(attrs=attrs)


class VehicleForm(StyledModelForm):
    class Meta:
        model = Vehicle
        fields = '__all__'
        widgets = {'photo': image_widget()}

class ParcelForm(StyledModelForm):
    class Meta:
        model = Parcel
        exclude = ['received_at', 'collected_at', 'received_by']
        widgets = {'photo': image_widget()}

class VendorAMCForm(StyledModelForm):
    class Meta:
        model = VendorAMC
        fields = '__all__'
        widgets = {'start_date': forms.DateInput(attrs={'type':'date'}), 'renewal_date': forms.DateInput(attrs={'type':'date'})}

class ExpenseForm(StyledModelForm):
    class Meta:
        model = Expense
        exclude = ['created_by']
        widgets = {'expense_date': forms.DateInput(attrs={'type':'date'}), 'receipt': image_widget()}

class MoveRequestForm(StyledModelForm):
    class Meta:
        model = MoveRequest
        exclude = ['requested_by', 'created_at']
        widgets = {'requested_date': forms.DateInput(attrs={'type':'date'})}

class DomesticWorkerForm(StyledModelForm):
    class Meta:
        model = DomesticWorker
        fields = '__all__'
        widgets = {'photo': image_widget()}

class CertificateRequestForm(StyledModelForm):
    class Meta:
        model = CertificateRequest
        exclude = ['requested_by', 'requested_at']

class SocietyMeetingForm(StyledModelForm):
    class Meta:
        model = SocietyMeeting
        exclude = ['created_by']
        widgets = {'meeting_date': forms.DateTimeInput(attrs={'type':'datetime-local'})}

class PollForm(StyledModelForm):
    option_1 = forms.CharField(max_length=120)
    option_2 = forms.CharField(max_length=120)
    option_3 = forms.CharField(max_length=120, required=False)
    option_4 = forms.CharField(max_length=120, required=False)
    class Meta:
        model = Poll
        fields = ['question','description','closes_at','is_active']
        widgets = {'closes_at': forms.DateTimeInput(attrs={'type':'datetime-local'})}

class SocietyAssetForm(StyledModelForm):
    class Meta:
        model = SocietyAsset
        fields = '__all__'
        widgets = {'purchase_date': forms.DateInput(attrs={'type':'date'}), 'warranty_until': forms.DateInput(attrs={'type':'date'}), 'next_service_date': forms.DateInput(attrs={'type':'date'})}

class EmergencyContactForm(StyledModelForm):
    class Meta:
        model = EmergencyContact
        fields = '__all__'

class LostFoundForm(StyledModelForm):
    class Meta:
        model = LostFoundItem
        exclude = ['reported_by','reported_at']
        widgets = {'photo': image_widget()}

class SocietyEventForm(StyledModelForm):
    class Meta:
        model = SocietyEvent
        fields = '__all__'
        widgets = {'event_date': forms.DateTimeInput(attrs={'type':'datetime-local'}), 'poster': image_widget()}
