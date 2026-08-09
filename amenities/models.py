from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Amenity(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField(default=1)
    booking_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    open_time = models.TimeField(default='06:00')
    close_time = models.TimeField(default='22:00')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return self.name


class AmenityBooking(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', _('Requested')
        CONFIRMED = 'CONFIRMED', _('Confirmed')
        CANCELLED = 'CANCELLED', _('Cancelled')
        COMPLETED = 'COMPLETED', _('Completed')

    amenity = models.ForeignKey(Amenity, on_delete=models.CASCADE, related_name='bookings')
    booked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='amenity_bookings')
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.REQUESTED)
    notes = models.TextField(blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date', '-start_time']

    def __str__(self):
        return f"{self.amenity.name} - {self.booking_date} ({self.booked_by})"
