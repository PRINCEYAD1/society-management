from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'posted_by', 'posted_on', 'pinned')
    list_filter = ('category', 'pinned')
    search_fields = ('title', 'content')
