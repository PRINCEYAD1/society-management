from django import forms
from core.mixins import BootstrapFormMixin
from .models import User


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'photo']
