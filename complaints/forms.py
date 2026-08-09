from django import forms
from core.mixins import BootstrapFormMixin
from .models import Complaint, ComplaintComment


class ComplaintForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['flat', 'category', 'title', 'description', 'priority']


class ComplaintCommentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ComplaintComment
        fields = ['comment']
        widgets = {'comment': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Add a comment...'})}


class ComplaintStatusForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'assigned_to']
