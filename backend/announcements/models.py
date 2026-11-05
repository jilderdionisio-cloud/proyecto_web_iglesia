from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone


class AnnouncementQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()), is_published=True)


class Announcement(models.Model):
    title = models.CharField('título', max_length=160)
    body = models.TextField('contenido')
    is_published = models.BooleanField('publicado', default=False)
    published_at = models.DateTimeField('fecha de publicación', null=True, blank=True)
    expires_at = models.DateTimeField('vigente hasta', null=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        ordering = ('-published_at', '-created_at')

    def __str__(self):
        return self.title
