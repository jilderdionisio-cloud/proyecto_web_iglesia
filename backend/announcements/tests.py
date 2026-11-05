from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Announcement


class AnnouncementApiTests(APITestCase):
    def setUp(self):
        self.secretary = User.objects.create_user(email='secretaria@iglesia.test', password='ClaveSegura123!', role=User.Role.SECRETARY)
        self.coordinator = User.objects.create_user(email='coordinador@iglesia.test', password='ClaveSegura123!', role=User.Role.COORDINATOR)
        self.client.force_authenticate(self.secretary)

    def test_create_publish_edit_and_delete(self):
        create = self.client.post('/api/announcements/', {'title': 'Ayuno', 'body': 'Este viernes'}, format='json')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertFalse(create.data['is_published'])
        self.assertEqual(create.data['author_name'], self.secretary.email)
        announcement = create.data['id']

        publish = self.client.post(f'/api/announcements/{announcement}/publish/')
        self.assertTrue(publish.data['is_published'])
        self.assertIsNotNone(publish.data['published_at'])

        edit = self.client.patch(f'/api/announcements/{announcement}/', {'title': 'Ayuno congregacional', 'is_published': False}, format='json')
        self.assertEqual(edit.data['title'], 'Ayuno congregacional')
        self.assertTrue(edit.data['is_published'])

        self.assertEqual(self.client.delete(f'/api/announcements/{announcement}/').status_code, status.HTTP_204_NO_CONTENT)

    def test_only_visible_announcements_reach_other_roles(self):
        Announcement.objects.create(title='Borrador', body='x', author=self.secretary)
        Announcement.objects.create(title='Publicado', body='x', author=self.secretary, is_published=True, published_at=timezone.now())
        Announcement.objects.create(title='Vencido', body='x', author=self.secretary, is_published=True, published_at=timezone.now(), expires_at=timezone.now() - timedelta(days=1))
        self.assertEqual(len(self.client.get('/api/announcements/').data), 3)
        self.assertEqual(len(self.client.get('/api/announcements/?visible=true').data), 1)

        self.client.force_authenticate(self.coordinator)
        listed = self.client.get('/api/announcements/')
        self.assertEqual([item['title'] for item in listed.data], ['Publicado'])
        draft = Announcement.objects.get(title='Borrador')
        self.assertEqual(self.client.get(f'/api/announcements/{draft.pk}/').status_code, status.HTTP_404_NOT_FOUND)

    def test_unpublish_hides_announcement(self):
        item = Announcement.objects.create(title='Aviso', body='x', author=self.secretary, is_published=True, published_at=timezone.now())
        self.client.post(f'/api/announcements/{item.pk}/unpublish/')
        self.client.force_authenticate(self.coordinator)
        self.assertEqual(self.client.get('/api/announcements/').data, [])

    def test_expiration_rules(self):
        past = (timezone.now() - timedelta(days=1)).isoformat()
        self.assertEqual(self.client.post('/api/announcements/', {'title': 'A', 'body': 'x', 'expires_at': past}, format='json').status_code, status.HTTP_400_BAD_REQUEST)
        expired = Announcement.objects.create(title='B', body='x', author=self.secretary, expires_at=timezone.now() - timedelta(days=1))
        self.assertEqual(self.client.post(f'/api/announcements/{expired.pk}/publish/').status_code, status.HTTP_400_BAD_REQUEST)

    def test_required_fields(self):
        response = self.client.post('/api/announcements/', {'title': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('body', response.data)

    def test_other_roles_cannot_write(self):
        item = Announcement.objects.create(title='Aviso', body='x', author=self.secretary, is_published=True, published_at=timezone.now())
        for role in (User.Role.COORDINATOR, User.Role.TREASURER):
            self.client.force_authenticate(User.objects.create_user(email=f'otro-{role}@iglesia.test', password='ClaveSegura123!', role=role))
            self.assertEqual(self.client.post('/api/announcements/', {'title': 'A', 'body': 'x'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.patch(f'/api/announcements/{item.pk}/', {'title': 'A'}, format='json').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.delete(f'/api/announcements/{item.pk}/').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.post(f'/api/announcements/{item.pk}/unpublish/').status_code, status.HTTP_403_FORBIDDEN)
