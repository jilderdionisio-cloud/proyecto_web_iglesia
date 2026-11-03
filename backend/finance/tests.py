from rest_framework import status
from rest_framework.test import APITestCase
from accounts.models import User

class DonationTests(APITestCase):
    def setUp(self):
        self.treasurer=User.objects.create_user(email='tesorero@test.com',password='ClaveSegura123!',role=User.Role.TREASURER)
        self.secretary=User.objects.create_user(email='secretaria@test.com',password='ClaveSegura123!',role=User.Role.SECRETARY)
    def test_finance_permission_and_anonymous_donation(self):
        self.client.force_authenticate(self.secretary)
        self.assertEqual(self.client.get('/api/donations/').status_code,status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.treasurer)
        response=self.client.post('/api/donations/',{'received_at':'2026-01-01','amount':'100.00','concept':'Ofrenda','method':'cash','donor_name':'Ana','is_anonymous':True},format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(response.data['display_donor'],'Anónimo')
