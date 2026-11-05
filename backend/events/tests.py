from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from attendance.models import AttendanceSession
from .models import Event


class EventApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='pastor@iglesia.test', password='ClaveSegura123!', role=User.Role.PASTOR)
        self.coordinator = User.objects.create_user(email='coordinador@iglesia.test', password='ClaveSegura123!', role=User.Role.COORDINATOR)
        self.starts_at = timezone.now() + timedelta(days=2)
        self.client.force_authenticate(self.user)

    def create_event(self, **extra):
        return Event.objects.create(**{'title': 'Culto', 'starts_at': self.starts_at, 'location': 'Templo', 'responsible': self.user, **extra})

    def test_create_and_cancel_event(self):
        create = self.client.post('/api/events/', {'title': 'Culto dominical', 'starts_at': self.starts_at.isoformat(), 'location': 'Templo'}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get()
        self.assertEqual(event.responsible, self.user)

        cancel = self.client.post(f'/api/events/{event.pk}/cancel/', {'reason': 'Clima'}, format='json')
        self.assertEqual(cancel.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel.data['status'], Event.Status.CANCELLED)

        again = self.client.post(f'/api/events/{event.pk}/cancel/', {}, format='json')
        self.assertEqual(again.status_code, status.HTTP_400_BAD_REQUEST)
        edit = self.client.patch(f'/api/events/{event.pk}/', {'title': 'Otro'}, format='json')
        self.assertEqual(edit.status_code, status.HTTP_400_BAD_REQUEST)

    def test_responsible_can_be_selected(self):
        create = self.client.post('/api/events/', {'title': 'Retiro', 'starts_at': self.starts_at.isoformat(), 'location': 'Campo', 'responsible': self.coordinator.pk}, format='json')
        self.assertEqual(create.data['responsible'], self.coordinator.pk)
        self.assertEqual(create.data['responsible_name'], self.coordinator.email)

    def test_inactive_responsible_is_rejected(self):
        self.coordinator.is_active = False
        self.coordinator.save()
        create = self.client.post('/api/events/', {'title': 'Retiro', 'starts_at': self.starts_at.isoformat(), 'location': 'Campo', 'responsible': self.coordinator.pk}, format='json')
        self.assertEqual(create.status_code, status.HTTP_400_BAD_REQUEST)

    def test_end_must_follow_start_even_on_partial_update(self):
        event = self.create_event(ends_at=self.starts_at + timedelta(hours=2))
        update = self.client.patch(f'/api/events/{event.pk}/', {'starts_at': (self.starts_at + timedelta(days=1)).isoformat()}, format='json')
        self.assertEqual(update.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('ends_at', update.data)

    def test_filters_by_range_and_upcoming(self):
        self.create_event()
        self.create_event(title='Pasado', starts_at=timezone.now() - timedelta(days=40))
        self.create_event(title='Cancelado', status=Event.Status.CANCELLED)
        upcoming = self.client.get('/api/events/?upcoming=true')
        self.assertEqual([event['title'] for event in upcoming.data], ['Culto'])
        day = timezone.localtime(self.starts_at).date().isoformat()
        ranged = self.client.get(f'/api/events/?from={day}&to={day}')
        self.assertEqual(len(ranged.data), 2)
        self.assertEqual(self.client.get('/api/events/?from=ayer').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get('/api/events/?from=2026-02-01&to=2026-01-01').status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_with_attendance_cannot_be_deleted(self):
        event = self.create_event()
        AttendanceSession.objects.create(event=event, date=timezone.localdate(), created_by=self.user)
        self.assertEqual(self.client.delete(f'/api/events/{event.pk}/').status_code, status.HTTP_409_CONFLICT)
        other = self.create_event(title='Sin asistencia')
        self.assertEqual(self.client.delete(f'/api/events/{other.pk}/').status_code, status.HTTP_204_NO_CONTENT)

    def test_coordinator_only_changes_own_events(self):
        own = self.create_event(responsible=self.coordinator)
        foreign = self.create_event()
        self.client.force_authenticate(self.coordinator)
        self.assertEqual(self.client.patch(f'/api/events/{own.pk}/', {'title': 'Mío', 'responsible': self.user.pk}, format='json').status_code, status.HTTP_200_OK)
        own.refresh_from_db()
        self.assertEqual(own.responsible, self.coordinator)
        self.assertEqual(self.client.patch(f'/api/events/{foreign.pk}/', {'title': 'Ajeno'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f'/api/events/{foreign.pk}/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.post(f'/api/events/{foreign.pk}/cancel/', {}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        create = self.client.post('/api/events/', {'title': 'Taller', 'starts_at': self.starts_at.isoformat(), 'location': 'Salón', 'responsible': self.user.pk}, format='json')
        self.assertEqual(create.data['responsible'], self.coordinator.pk)

    def test_treasurer_reads_but_cannot_write(self):
        self.client.force_authenticate(User.objects.create_user(email='tesorera@iglesia.test', password='ClaveSegura123!', role=User.Role.TREASURER))
        self.assertEqual(self.client.get('/api/events/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post('/api/events/', {'title': 'X', 'starts_at': self.starts_at.isoformat(), 'location': 'Y'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
