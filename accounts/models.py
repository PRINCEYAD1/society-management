from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Society Admin')
        COMMITTEE = 'COMMITTEE', _('Committee Member')
        RESIDENT = 'RESIDENT', _('Resident')
        SECURITY = 'SECURITY', _('Security Guard')
        STAFF = 'STAFF', _('Staff')

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RESIDENT, verbose_name=_('role'))
    phone_number = models.CharField(max_length=15, blank=True, verbose_name=_('phone number'))
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True, verbose_name=_('photo'))

    def is_admin_or_committee(self):
        return self.role in (self.Role.ADMIN, self.Role.COMMITTEE)

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
