from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from members.models import Member


class MinistryApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='admin@iglesia.test', password='ClaveSegura123!', role=User.Role.ADMINISTRATOR)
        self.member = Member.objects.create(first_name='Sofía', last_name='Ramírez')
        self.client.force_authenticate(self.user)

    def test_create_ministry_and_assign_member(self):
        create = self.client.post('/api/ministries/', {'name': 'Alabanza', 'description': 'Música', 'coordinator': self.user.pk}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        assign = self.client.post(f"/api/ministries/{create.data['id']}/members/", {'member': self.member.pk}, format='json')
        self.assertEqual(assign.status_code, status.HTTP_200_OK)
        self.assertEqual(assign.data['members'][0]['member_id'], self.member.pk)
