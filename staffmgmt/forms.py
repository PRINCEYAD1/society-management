from django import forms
from core.mixins import BootstrapFormMixin
from .models import StaffMember, Attendance


class StaffMemberForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = StaffMember
        fields = ['name', 'category', 'phone_number', 'address', 'id_proof_number', 'photo', 'monthly_salary', 'is_active']


class AttendanceForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['date', 'status']
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
