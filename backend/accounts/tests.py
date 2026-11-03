from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):
    def test_register_and_login_with_email(self):
        admin = User.objects.create_user(email='admin@iglesia.test', password='ClaveSegura123!', role=User.Role.ADMINISTRATOR)
        self.client.force_authenticate(admin)
        register = self.client.post(reverse('register'), {
            'email': 'coordinador@iglesia.test',
            'password': 'ClaveSegura123!',
            'first_name': 'Ana',
            'role': User.Role.COORDINATOR,
        }, format='json')
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertEqual(register.data['role'], User.Role.COORDINATOR)

        self.client.force_authenticate(user=None)
        login = self.client.post(reverse('login'), {
            'email': 'coordinador@iglesia.test', 'password': 'ClaveSegura123!'
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn('access', login.data)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_only_admin_can_create_user(self):
        data = {'email': 'nuevo@iglesia.test', 'password': 'ClaveSegura123!', 'role': User.Role.SECRETARY}
        self.assertEqual(self.client.post(reverse('register'), data, format='json').status_code, status.HTTP_401_UNAUTHORIZED)
        admin = User.objects.create_user(email='admin@iglesia.test', password='ClaveSegura123!', role=User.Role.ADMINISTRATOR)
        self.client.force_authenticate(admin)
        response = self.client.post(reverse('register'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email=data['email']).role, User.Role.SECRETARY)
