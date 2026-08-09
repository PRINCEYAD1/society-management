from django.db import models
from django.utils.translation import gettext_lazy as _


class StaffMember(models.Model):
    class Category(models.TextChoices):
        SECURITY = 'SECURITY', _('Security Guard')
        HOUSEKEEPING = 'HOUSEKEEPING', _('Housekeeping')
        PLUMBER = 'PLUMBER', _('Plumber')
        ELECTRICIAN = 'ELECTRICIAN', _('Electrician')
        GARDENER = 'GARDENER', _('Gardener')
        MANAGER = 'MANAGER', _('Society Manager')
        OTHER = 'OTHER', _('Other')

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    id_proof_number = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='staff_photos/', blank=True, null=True)
    monthly_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_joined = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', _('Present')
        ABSENT = 'ABSENT', _('Absent')
        HALF_DAY = 'HALF_DAY', _('Half Day')
        LEAVE = 'LEAVE', _('On Leave')

    staff = models.ForeignKey(StaffMember, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)

    class Meta:
        unique_together = ('staff', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.staff.name} - {self.date} - {self.get_status_display()}"
