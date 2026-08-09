from django.contrib import admin
from .models import Visitor


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'visiting_flat', 'purpose', 'status', 'check_in_time', 'check_out_time')
    list_filter = ('status', 'purpose')
    search_fields = ('name', 'vehicle_number', 'phone_number')
