import os
import shutil
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import ChurchProfile, ServiceSchedule

MEDIA_ROOT = tempfile.mkdtemp()


def image_file(name='logo.png', image_format='PNG'):
    output = BytesIO()
    Image.new('RGB', (8, 8), '#143c35').save(output, image_format)
    return SimpleUploadedFile(name, output.getvalue(), content_type=f'image/{image_format.lower()}')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class ChurchApiTests(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.admin = User.objects.create_user(email='admin@iglesia.test', password='ClaveSegura123!', role=User.Role.ADMINISTRATOR)

    def test_profile_is_public_to_read(self):
        response = self.client.get('/api/church/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Mi Iglesia')
        self.assertEqual(response.data['schedules'], [])

    def test_admin_updates_profile_and_it_stays_single(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch('/api/church/', {'name': 'Iglesia Central', 'phone': '555', 'address': 'Calle 1', 'email': 'hola@iglesia.test'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.patch('/api/church/', {'city': 'Mérida'}, format='json')
        profile = ChurchProfile.objects.get()
        self.assertEqual((profile.pk, profile.name, profile.city), (1, 'Iglesia Central', 'Mérida'))

    def test_invalid_contact_data_is_rejected(self):
        self.client.force_authenticate(self.admin)
        response = self.client.patch('/api/church/', {'email': 'no-es-correo', 'website': 'nada'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {'email', 'website'})

    def test_logo_upload_replace_and_remove(self):
        self.client.force_authenticate(self.admin)
        upload = self.client.patch('/api/church/', {'logo': image_file()}, format='multipart')
        self.assertEqual(upload.status_code, status.HTTP_200_OK)
        self.assertTrue(upload.data['logo'].startswith('/media/church/'))
        first = ChurchProfile.objects.get().logo
        storage, first_name = first.storage, first.name
        self.assertTrue(storage.exists(first_name))

        self.client.patch('/api/church/', {'logo': image_file('otro.jpg', 'JPEG')}, format='multipart')
        self.assertFalse(storage.exists(first_name))

        removed = self.client.patch('/api/church/', {'remove_logo': True}, format='json')
        self.assertIsNone(removed.data['logo'])
        self.assertFalse(ChurchProfile.objects.get().logo)

    def test_logo_validation(self):
        self.client.force_authenticate(self.admin)
        fake = SimpleUploadedFile('logo.png', b'<script>alert(1)</script>', content_type='image/png')
        self.assertEqual(self.client.patch('/api/church/', {'logo': fake}, format='multipart').status_code, status.HTTP_400_BAD_REQUEST)
        gif = image_file('logo.gif', 'GIF')
        self.assertEqual(self.client.patch('/api/church/', {'logo': gif}, format='multipart').status_code, status.HTTP_400_BAD_REQUEST)
        output = BytesIO()
        Image.frombytes('RGB', (1000, 1000), os.urandom(3_000_000)).save(output, 'PNG')
        big = SimpleUploadedFile('grande.png', output.getvalue(), content_type='image/png')
        self.assertEqual(self.client.patch('/api/church/', {'logo': big}, format='multipart').status_code, status.HTTP_400_BAD_REQUEST)

    def test_schedules_crud(self):
        self.client.force_authenticate(self.admin)
        create = self.client.post('/api/church/schedules/', {'day': 6, 'name': 'Culto', 'starts_at': '10:00', 'ends_at': '12:00'}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data['day_label'], 'Domingo')
        self.assertEqual(len(self.client.get('/api/church/').data['schedules']), 1)
        invalid = self.client.post('/api/church/schedules/', {'day': 6, 'name': 'Culto', 'starts_at': '10:00', 'ends_at': '09:00'}, format='json')
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.post('/api/church/schedules/', {'day': 9, 'name': 'X', 'starts_at': '10:00'}, format='json').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.delete(f"/api/church/schedules/{create.data['id']}/").status_code, status.HTTP_204_NO_CONTENT)

    def test_only_administrators_change_the_profile(self):
        schedule = ServiceSchedule.objects.create(day=6, name='Culto', starts_at='10:00')
        self.assertEqual(self.client.patch('/api/church/', {'name': 'X'}, format='json').status_code, status.HTTP_401_UNAUTHORIZED)
        for role in (User.Role.PASTOR, User.Role.SECRETARY, User.Role.TREASURER, User.Role.COORDINATOR):
            self.client.force_authenticate(User.objects.create_user(email=f'{role}@iglesia.test', password='ClaveSegura123!', role=role))
            self.assertEqual(self.client.patch('/api/church/', {'name': 'X'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.post('/api/church/schedules/', {'day': 1, 'name': 'X', 'starts_at': '10:00'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.delete(f'/api/church/schedules/{schedule.pk}/').status_code, status.HTTP_403_FORBIDDEN)
