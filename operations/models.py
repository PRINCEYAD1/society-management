from django.conf import settings
from django.db import models
from core.models import Flat


class Vehicle(models.Model):
    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='vehicles')
    owner_name = models.CharField(max_length=120)
    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=30, choices=[('CAR','Car'),('BIKE','Bike'),('OTHER','Other')], default='CAR')
    parking_slot = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.vehicle_number} - {self.flat}'


class Parcel(models.Model):
    class Status(models.TextChoices):
        RECEIVED = 'RECEIVED', 'Received at Gate'
        NOTIFIED = 'NOTIFIED', 'Resident Notified'
        COLLECTED = 'COLLECTED', 'Collected'

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='parcels')
    recipient_name = models.CharField(max_length=120)
    courier_name = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='parcels/', blank=True, null=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.RECEIVED)
    received_at = models.DateTimeField(auto_now_add=True)
    collected_at = models.DateTimeField(blank=True, null=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.recipient_name} - {self.flat}'


class VendorAMC(models.Model):
    service_name = models.CharField(max_length=120)
    vendor_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField()
    renewal_date = models.DateField()
    document = models.FileField(upload_to='vendor_amc/', blank=True, null=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['renewal_date']

    def __str__(self):
        return f'{self.service_name} - {self.vendor_name}'


class Expense(models.Model):
    CATEGORY_CHOICES = [('UTILITIES','Utilities'),('REPAIR','Repair & Maintenance'),('SALARY','Salary'),('VENDOR','Vendor'),('EVENT','Event'),('OTHER','Other')]
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OTHER')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    vendor = models.CharField(max_length=150, blank=True)
    receipt = models.ImageField(upload_to='expense_receipts/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        ordering = ['-expense_date']

    def __str__(self):
        return self.title


class MoveRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        APPROVED = 'APPROVED', 'Approved'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='move_requests')
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    move_type = models.CharField(max_length=10, choices=[('MOVE_IN','Move In'),('MOVE_OUT','Move Out')])
    requested_date = models.DateField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.REQUESTED)
    document = models.FileField(upload_to='move_requests/', blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.get_move_type_display()} - {self.flat}'
