from django import forms
from core.mixins import BootstrapFormMixin
from .models import Notice


class NoticeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'category', 'pinned', 'attachment']
