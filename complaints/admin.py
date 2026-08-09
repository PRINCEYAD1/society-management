from django.contrib import admin
from .models import Complaint, ComplaintComment


class ComplaintCommentInline(admin.TabularInline):
    model = ComplaintComment
    extra = 0


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('title', 'raised_by', 'flat', 'category', 'priority', 'status', 'created_on')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description')
    inlines = [ComplaintCommentInline]
