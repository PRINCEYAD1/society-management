from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Society(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    registration_number = models.CharField(max_length=100, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=15, blank=True)

    class Meta:
        verbose_name_plural = 'Societies'

    def __str__(self):
        return self.name


class Building(models.Model):
    society = models.ForeignKey(Society, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField(max_length=100)
    total_floors = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.name} - {self.society.name}"


class Flat(models.Model):
    class OwnershipType(models.TextChoices):
        OWNER = 'OWNER', _('Owner Occupied')
        RENTED = 'RENTED', _('Rented')
        VACANT = 'VACANT', _('Vacant')

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='flats')
    flat_number = models.CharField(max_length=20)
    floor = models.PositiveIntegerField(default=0)
    area_sqft = models.PositiveIntegerField(default=0)
    ownership_type = models.CharField(max_length=10, choices=OwnershipType.choices, default=OwnershipType.OWNER)

    class Meta:
        unique_together = ('building', 'flat_number')
        ordering = ['building', 'floor', 'flat_number']

    def __str__(self):
        return f"{self.building.name}-{self.flat_number}"


class ResidentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resident_profile')
    flat = models.ForeignKey(Flat, on_delete=models.SET_NULL, null=True, blank=True, related_name='residents')
    is_primary_contact = models.BooleanField(default=True)
    move_in_date = models.DateField(null=True, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.user} - {self.flat}"
