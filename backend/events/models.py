from django.conf import settings
from django.db import models


class Event(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Programado'
        CANCELLED = 'cancelled', 'Cancelado'

    title = models.CharField('título', max_length=160)
    description = models.TextField(blank=True)
    starts_at = models.DateTimeField('inicio')
    ends_at = models.DateTimeField('fin', null=True, blank=True)
    location = models.CharField('lugar', max_length=200)
    responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='responsible_events')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('starts_at',)

    def __str__(self):
        return self.title
