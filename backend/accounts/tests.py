from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import User


class AuthenticationTests(APITestCase):
    def test_register_and_login_with_email(self):
        register = self.client.post(reverse('register'), {
            'email': 'coordinador@iglesia.test',
            'password': 'ClaveSegura123!',
            'first_name': 'Ana',
        }, format='json')
        self.assertEqual(register.status_code, status.HTTP_201_CREATED)
        self.assertEqual(register.data['role'], User.Role.COORDINATOR)

        login = self.client.post(reverse('login'), {
            'email': 'coordinador@iglesia.test', 'password': 'ClaveSegura123!'
        }, format='json')
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.assertIn('access', login.data)

    def test_me_requires_authentication(self):
        response = self.client.get(reverse('me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
