from django import forms
from core.mixins import BootstrapFormMixin
from .models import Amenity, AmenityBooking


class AmenityForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Amenity
        fields = ['name', 'description', 'capacity', 'booking_fee', 'open_time', 'close_time', 'is_active']
        widgets = {
            'open_time': forms.TimeInput(attrs={'type': 'time'}),
            'close_time': forms.TimeInput(attrs={'type': 'time'}),
        }


class AmenityBookingForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = AmenityBooking
        fields = ['booking_date', 'start_time', 'end_time', 'notes']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
