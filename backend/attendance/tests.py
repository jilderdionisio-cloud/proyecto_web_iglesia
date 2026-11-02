from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from events.models import Event
from members.models import Member


class AttendanceApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='secretaria@iglesia.test', password='ClaveSegura123!', role=User.Role.SECRETARY)
        self.event = Event.objects.create(title='Culto', starts_at=timezone.now() + timedelta(days=1), location='Templo', responsible=self.user)
        self.member = Member.objects.create(first_name='Ana', last_name='Pérez')
        Member.objects.create(first_name='Luis', last_name='Díaz')
        self.client.force_authenticate(self.user)

    def test_create_mark_and_query_attendance(self):
        create = self.client.post('/api/attendance-sessions/', {'event': self.event.pk, 'date': timezone.localdate().isoformat()}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(create.data['records']), 2)
        session_id = create.data['id']

        update = self.client.put(f'/api/attendance-sessions/{session_id}/records/', {'records': [{'member': self.member.pk, 'status': 'present'}]}, format='json')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(update.data['present_count'], 1)

        history = self.client.get(f'/api/attendance-history/?event={self.event.pk}&member={self.member.pk}')
        self.assertEqual(len(history.data), 1)
        self.assertEqual(history.data[0]['status'], 'present')

        summary = self.client.get('/api/attendance-history/summary/?period=week')
        self.assertEqual(summary.data['present'], 1)
        self.assertEqual(summary.data['absent'], 1)
