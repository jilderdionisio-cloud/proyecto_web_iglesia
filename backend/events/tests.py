from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Event


class EventApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='pastor@iglesia.test', password='ClaveSegura123!', role=User.Role.PASTOR)
        self.client.force_authenticate(self.user)

    def test_create_and_cancel_event(self):
        starts_at = timezone.now() + timedelta(days=2)
        create = self.client.post('/api/events/', {'title': 'Culto dominical', 'starts_at': starts_at.isoformat(), 'location': 'Templo'}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        event = Event.objects.get()
        self.assertEqual(event.responsible, self.user)

        cancel = self.client.post(f'/api/events/{event.pk}/cancel/', {'reason': 'Clima'}, format='json')
        self.assertEqual(cancel.status_code, status.HTTP_200_OK)
        self.assertEqual(cancel.data['status'], Event.Status.CANCELLED)
