from django.contrib import admin
from .models import MaintenanceChargeTemplate, Invoice, Payment


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin.register(MaintenanceChargeTemplate)
class MaintenanceChargeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'is_active')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'flat', 'title', 'amount', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('flat__flat_number', 'title')
    inlines = [PaymentInline]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'amount', 'method', 'paid_on', 'recorded_by')
    list_filter = ('method', 'paid_on')
