from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notice(models.Model):
    class Category(models.TextChoices):
        GENERAL = 'GENERAL', _('General')
        MAINTENANCE = 'MAINTENANCE', _('Maintenance')
        EVENT = 'EVENT', _('Event')
        URGENT = 'URGENT', _('Urgent')
        MEETING = 'MEETING', _('Meeting')

    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.GENERAL)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    posted_on = models.DateTimeField(auto_now_add=True)
    pinned = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='notice_attachments/', blank=True, null=True)

    class Meta:
        ordering = ['-pinned', '-posted_on']

    def __str__(self):
        return self.title
