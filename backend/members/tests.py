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

    def test_edit_and_reactivate_member(self):
        member = Member.objects.create(first_name='Luis', last_name='Díaz', is_active=False)
        update = self.client.patch(f'/api/members/{member.pk}/', {'address': 'Calle 1', 'birth_date': '1990-05-02', 'notes': 'Bautizado'}, format='json')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        self.assertEqual(update.data['address'], 'Calle 1')
        activate = self.client.post(f'/api/members/{member.pk}/activate/')
        self.assertTrue(activate.data['is_active'])

    def test_pagination_is_optional(self):
        Member.objects.bulk_create([Member(first_name=f'Nombre{index}', last_name='Prueba') for index in range(25)])
        self.assertEqual(len(self.client.get('/api/members/').data), 25)
        page = self.client.get('/api/members/?page=2&page_size=10')
        self.assertEqual(page.data['count'], 25)
        self.assertEqual(len(page.data['results']), 10)
        self.assertEqual(self.client.get('/api/members/?page=99').status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_data_is_rejected(self):
        invalid = self.client.post('/api/members/', {'first_name': '', 'email': 'no-es-correo'}, format='json')
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('last_name', invalid.data)
        self.assertIn('email', invalid.data)

    def test_read_only_roles_cannot_write(self):
        member = Member.objects.create(first_name='Ana', last_name='Ruiz')
        for role in (User.Role.COORDINATOR, User.Role.TREASURER):
            self.client.force_authenticate(User.objects.create_user(email=f'{role}@iglesia.test', password='ClaveSegura123!', role=role))
            self.assertEqual(self.client.get('/api/members/').status_code, status.HTTP_200_OK)
            self.assertEqual(self.client.post('/api/members/', {'first_name': 'X', 'last_name': 'Y'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.patch(f'/api/members/{member.pk}/', {'notes': 'x'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.delete(f'/api/members/{member.pk}/').status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_access_is_rejected(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/members/').status_code, status.HTTP_401_UNAUTHORIZED)
