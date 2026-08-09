from django.contrib import admin
from .models import Amenity, AmenityBooking


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'booking_fee', 'is_active')


@admin.register(AmenityBooking)
class AmenityBookingAdmin(admin.ModelAdmin):
    list_display = ('amenity', 'booked_by', 'booking_date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'amenity')
