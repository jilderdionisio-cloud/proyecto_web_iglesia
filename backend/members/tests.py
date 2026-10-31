from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Member


class MemberApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='secretaria@iglesia.test', password='ClaveSegura123!', role=User.Role.SECRETARY)
        self.client.force_authenticate(self.user)

    def test_create_filter_and_deactivate_member(self):
        create = self.client.post('/api/members/', {'first_name': 'María', 'last_name': 'López', 'email': 'maria@test.com'}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        member = Member.objects.get()
        self.assertTrue(member.is_active)

        filtered = self.client.get('/api/members/?active=true&search=María')
        self.assertEqual(len(filtered.data), 1)

        delete = self.client.delete(f'/api/members/{member.pk}/')
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        member.refresh_from_db()
        self.assertFalse(member.is_active)
