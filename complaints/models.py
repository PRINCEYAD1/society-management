from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Flat


class Complaint(models.Model):
    class Category(models.TextChoices):
        PLUMBING = 'PLUMBING', _('Plumbing')
        ELECTRICAL = 'ELECTRICAL', _('Electrical')
        SECURITY = 'SECURITY', _('Security')
        CLEANLINESS = 'CLEANLINESS', _('Cleanliness')
        NOISE = 'NOISE', _('Noise')
        PARKING = 'PARKING', _('Parking')
        OTHER = 'OTHER', _('Other')

    class Status(models.TextChoices):
        OPEN = 'OPEN', _('Open')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        RESOLVED = 'RESOLVED', _('Resolved')
        CLOSED = 'CLOSED', _('Closed')

    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')

    raised_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='complaints')
    flat = models.ForeignKey(Flat, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.OPEN)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_complaints'
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ComplaintComment(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment on {self.complaint}"
