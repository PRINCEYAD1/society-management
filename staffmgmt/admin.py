from django.contrib import admin
from .models import StaffMember, Attendance


class AttendanceInline(admin.TabularInline):
    model = Attendance
    extra = 0


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'phone_number', 'monthly_salary', 'is_active')
    list_filter = ('category', 'is_active')
    inlines = [AttendanceInline]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('staff', 'date', 'status')
    list_filter = ('status', 'date')
