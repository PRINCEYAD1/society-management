from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Flat


class Visitor(models.Model):
    class Purpose(models.TextChoices):
        GUEST = 'GUEST', _('Guest')
        DELIVERY = 'DELIVERY', _('Delivery')
        CAB = 'CAB', _('Cab/Taxi')
        SERVICE = 'SERVICE', _('Service/Repair')
        VENDOR = 'VENDOR', _('Vendor')
        OTHER = 'OTHER', _('Other')

    class Status(models.TextChoices):
        PENDING_APPROVAL = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        DENIED = 'DENIED', _('Denied')
        CHECKED_IN = 'CHECKED_IN', _('Checked In')
        CHECKED_OUT = 'CHECKED_OUT', _('Checked Out')

    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    purpose = models.CharField(max_length=15, choices=Purpose.choices, default=Purpose.GUEST)
    visiting_flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='visitors')
    vehicle_number = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to='visitor_photos/', blank=True, null=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING_APPROVAL)
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='logged_visitors'
    )
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return f"{self.name} -> {self.visiting_flat} ({self.get_status_display()})"
