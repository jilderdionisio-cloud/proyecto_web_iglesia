from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from members.models import Member
from .models import Ministry, MinistryActivity


class MinistryApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='admin@iglesia.test', password='ClaveSegura123!', role=User.Role.ADMINISTRATOR)
        self.coordinator = User.objects.create_user(email='coordinador@iglesia.test', password='ClaveSegura123!', role=User.Role.COORDINATOR)
        self.member = Member.objects.create(first_name='Sofía', last_name='Ramírez')
        self.own = Ministry.objects.create(name='Jóvenes', coordinator=self.coordinator)
        self.foreign = Ministry.objects.create(name='Niños', coordinator=self.user)
        self.client.force_authenticate(self.user)

    def test_create_ministry_and_assign_member(self):
        create = self.client.post('/api/ministries/', {'name': 'Alabanza', 'description': 'Música', 'coordinator': self.user.pk}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        assign = self.client.post(f"/api/ministries/{create.data['id']}/members/", {'member': self.member.pk}, format='json')
        self.assertEqual(assign.status_code, status.HTTP_200_OK)
        self.assertEqual(assign.data['members'][0]['member_id'], self.member.pk)

        remove = self.client.delete(f"/api/ministries/{create.data['id']}/members/", {'member': self.member.pk}, format='json')
        self.assertEqual(remove.status_code, status.HTTP_204_NO_CONTENT)
        missing = self.client.delete(f"/api/ministries/{create.data['id']}/members/", {'member': self.member.pk}, format='json')
        self.assertEqual(missing.status_code, status.HTTP_404_NOT_FOUND)

    def test_rejects_inactive_coordinator_member_and_duplicate_name(self):
        self.coordinator.is_active = False
        self.coordinator.save()
        inactive = self.client.post('/api/ministries/', {'name': 'Otro', 'coordinator': self.coordinator.pk}, format='json')
        self.assertEqual(inactive.status_code, status.HTTP_400_BAD_REQUEST)
        duplicated = self.client.post('/api/ministries/', {'name': 'Niños', 'coordinator': self.user.pk}, format='json')
        self.assertEqual(duplicated.status_code, status.HTTP_400_BAD_REQUEST)
        self.member.is_active = False
        self.member.save()
        assign = self.client.post(f'/api/ministries/{self.own.pk}/members/', {'member': self.member.pk}, format='json')
        self.assertEqual(assign.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activity_crud_and_filter(self):
        create = self.client.post('/api/ministry-activities/', {'ministry': self.own.pk, 'title': 'Ensayo', 'date': '2026-11-10'}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data['ministry_name'], 'Jóvenes')
        self.assertEqual(len(self.client.get(f'/api/ministry-activities/?ministry={self.own.pk}').data), 1)
        self.assertEqual(len(self.client.get(f'/api/ministry-activities/?ministry={self.foreign.pk}').data), 0)
        activity = create.data['id']
        moved = self.client.patch(f'/api/ministry-activities/{activity}/', {'ministry': self.foreign.pk}, format='json')
        self.assertEqual(moved.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.delete(f'/api/ministry-activities/{activity}/').status_code, status.HTTP_204_NO_CONTENT)

    def test_coordinator_only_manages_own_ministry(self):
        self.client.force_authenticate(self.coordinator)
        self.assertEqual(self.client.post('/api/ministries/', {'name': 'Nuevo', 'coordinator': self.coordinator.pk}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f'/api/ministries/{self.own.pk}/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(f'/api/ministries/{self.foreign.pk}/', {'description': 'x'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.post(f'/api/ministries/{self.foreign.pk}/members/', {'member': self.member.pk}, format='json').status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(self.client.post(f'/api/ministries/{self.own.pk}/members/', {'member': self.member.pk}, format='json').status_code, status.HTTP_200_OK)
        self.client.patch(f'/api/ministries/{self.own.pk}/', {'description': 'Editado', 'coordinator': self.user.pk}, format='json')
        self.own.refresh_from_db()
        self.assertEqual(self.own.description, 'Editado')
        self.assertEqual(self.own.coordinator, self.coordinator)

    def test_coordinator_activities_are_scoped(self):
        foreign_activity = MinistryActivity.objects.create(ministry=self.foreign, title='Ajena', date='2026-11-10', created_by=self.user)
        self.client.force_authenticate(self.coordinator)
        own = self.client.post('/api/ministry-activities/', {'ministry': self.own.pk, 'title': 'Propia', 'date': '2026-11-10'}, format='json')
        self.assertEqual(own.status_code, status.HTTP_201_CREATED)
        foreign = self.client.post('/api/ministry-activities/', {'ministry': self.foreign.pk, 'title': 'No', 'date': '2026-11-10'}, format='json')
        self.assertEqual(foreign.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.patch(f'/api/ministry-activities/{foreign_activity.pk}/', {'title': 'x'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.delete(f'/api/ministry-activities/{foreign_activity.pk}/').status_code, status.HTTP_403_FORBIDDEN)

    def test_treasurer_reads_but_cannot_write(self):
        self.client.force_authenticate(User.objects.create_user(email='tesorera@iglesia.test', password='ClaveSegura123!', role=User.Role.TREASURER))
        self.assertEqual(self.client.get('/api/ministries/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.patch(f'/api/ministries/{self.own.pk}/', {'description': 'x'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.post('/api/ministry-activities/', {'ministry': self.own.pk, 'title': 'No', 'date': '2026-11-10'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
