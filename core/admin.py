from django.contrib import admin
from .models import Society, Building, Flat, ResidentProfile


@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_number', 'contact_email', 'contact_phone')


@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'society', 'total_floors')
    list_filter = ('society',)


@admin.register(Flat)
class FlatAdmin(admin.ModelAdmin):
    list_display = ('flat_number', 'building', 'floor', 'ownership_type', 'area_sqft')
    list_filter = ('building', 'ownership_type')
    search_fields = ('flat_number',)


@admin.register(ResidentProfile)
class ResidentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'flat', 'is_primary_contact', 'move_in_date')
    list_filter = ('is_primary_contact',)
