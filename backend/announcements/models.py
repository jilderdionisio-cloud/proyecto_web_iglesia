from django.conf import settings
from django.db import models

class Announcement(models.Model):
    title = models.CharField(max_length=160)
    body = models.TextField()
    published_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='announcements')
    class Meta: ordering = ('-published_at',)
