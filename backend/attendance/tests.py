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

    def create_session(self, date=None):
        return self.client.post('/api/attendance-sessions/', {'event': self.event.pk, 'date': (date or timezone.localdate()).isoformat()}, format='json')

    def test_create_mark_and_query_attendance(self):
        create = self.create_session()
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(create.data['records']), 2)
        session_id = create.data['id']

        update = self.client.put(f'/api/attendance-sessions/{session_id}/records/', {'records': [{'member': self.member.pk, 'status': 'present'}]}, format='json')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(update.data['present_count'], 1)

        history = self.client.get(f'/api/attendance-history/?event={self.event.pk}&member={self.member.pk}')
        self.assertEqual(len(history.data), 1)
        self.assertEqual(history.data[0]['status'], 'present')
        self.assertEqual(history.data[0]['event_name'], 'Culto')
        self.assertEqual(history.data[0]['date'], timezone.localdate().isoformat())
        self.assertEqual(history.data[0]['marked_by_name'], self.user.email)

        summary = self.client.get('/api/attendance-history/summary/?period=week')
        self.assertEqual(summary.data['present'], 1)
        self.assertEqual(summary.data['absent'], 1)

    def test_summary_period_uses_reference_date_as_end_of_range(self):
        today = timezone.localdate()
        self.create_session(today - timedelta(days=2))
        self.create_session(today - timedelta(days=20))
        week = self.client.get(f'/api/attendance-history/summary/?period=week&date={today.isoformat()}')
        month = self.client.get(f'/api/attendance-history/summary/?period=month&date={today.isoformat()}')
        self.assertEqual(week.data['absent'], 2)
        self.assertEqual(month.data['absent'], 4)

    def test_history_date_range(self):
        today = timezone.localdate()
        self.create_session(today - timedelta(days=10))
        self.create_session(today)
        ranged = self.client.get(f'/api/attendance-history/?from={today.isoformat()}')
        self.assertEqual(len(ranged.data), 2)
        sessions = self.client.get(f'/api/attendance-sessions/?to={(today - timedelta(days=1)).isoformat()}')
        self.assertEqual(len(sessions.data), 1)

    def test_invalid_parameters_return_400(self):
        for url in (
            '/api/attendance-history/summary/?period=year',
            '/api/attendance-history/summary/?date=mañana',
            '/api/attendance-history/?date=2026-13-40',
            '/api/attendance-history/?event=abc',
            '/api/attendance-sessions/?date=hoy',
        ):
            self.assertEqual(self.client.get(url).status_code, status.HTTP_400_BAD_REQUEST, url)

    def test_invalid_records_are_rejected(self):
        session_id = self.create_session().data['id']
        for records in (
            [{'member': 'abc', 'status': 'present'}],
            [{'member': self.member.pk, 'status': 'tarde'}],
            [{'member': 99999, 'status': 'present'}],
            [],
        ):
            response = self.client.put(f'/api/attendance-sessions/{session_id}/records/', {'records': records}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, records)

    def test_duplicate_session_and_cancelled_event_are_rejected(self):
        self.assertEqual(self.create_session().status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.create_session().status_code, status.HTTP_400_BAD_REQUEST)
        self.event.status = Event.Status.CANCELLED
        self.event.save()
        self.assertEqual(self.create_session(timezone.localdate() - timedelta(days=1)).status_code, status.HTTP_400_BAD_REQUEST)

    def test_treasurer_has_no_access(self):
        self.client.force_authenticate(User.objects.create_user(email='tesorera@iglesia.test', password='ClaveSegura123!', role=User.Role.TREASURER))
        self.assertEqual(self.client.get('/api/attendance-sessions/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get('/api/attendance-history/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.create_session().status_code, status.HTTP_403_FORBIDDEN)
