from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import Flat


class MaintenanceChargeTemplate(models.Model):
    """Defines recurring charge amounts, e.g. monthly maintenance per sqft or flat."""
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class Invoice(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')
        OVERDUE = 'OVERDUE', _('Overdue')
        PARTIAL = 'PARTIAL', _('Partially Paid')

    flat = models.ForeignKey(Flat, on_delete=models.CASCADE, related_name='invoices')
    charge_template = models.ForeignKey(MaintenanceChargeTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    issue_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-issue_date']

    def amount_paid(self):
        return sum(p.amount for p in self.payments.all())

    def balance(self):
        return self.amount - self.amount_paid()

    def __str__(self):
        return f"Invoice #{self.id} - {self.flat} - ₹{self.amount}"


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'CASH', _('Cash')
        UPI = 'UPI', _('UPI')
        BANK_TRANSFER = 'BANK', _('Bank Transfer')
        CHEQUE = 'CHEQUE', _('Cheque')
        CARD = 'CARD', _('Card')

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=Method.choices, default=Method.UPI)
    paid_on = models.DateField(auto_now_add=True)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment ₹{self.amount} for {self.invoice}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        invoice = self.invoice
        if invoice.balance() <= 0:
            invoice.status = Invoice.Status.PAID
        elif invoice.amount_paid() > 0:
            invoice.status = Invoice.Status.PARTIAL
        invoice.save(update_fields=['status'])
