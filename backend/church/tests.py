from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User

class ChurchProfileTests(APITestCase):
    def setUp(self): self.admin=User.objects.create_user(email='admin@iglesia.test',password='ClaveSegura123!',role=User.Role.ADMINISTRATOR)
    def test_profile_requires_admin_to_update(self):
        self.assertEqual(self.client.get('/api/church-profile/').status_code,status.HTTP_200_OK)
        self.assertEqual(self.client.put('/api/church-profile/',{'name':'Nueva'},format='json').status_code,status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.admin)
        response=self.client.put('/api/church-profile/',{'name':'Nueva Iglesia'},format='multipart')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['name'],'Nueva Iglesia')
