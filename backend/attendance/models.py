from django.conf import settings
from django.db import models

from events.models import Event
from members.models import Member


class AttendanceSession(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='attendance_sessions')
    date = models.DateField('fecha de asistencia')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_attendance_sessions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('event', 'date'), name='unique_event_attendance_date')]
        ordering = ('-date', '-id')

    def __str__(self):
        return f'{self.event} — {self.date}'


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'present', 'Presente'
        ABSENT = 'absent', 'Ausente'

    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='attendance_records')
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ABSENT)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='marked_attendance_records')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=('session', 'member'), name='unique_member_attendance_per_session')]
        ordering = ('member__last_name', 'member__first_name')
