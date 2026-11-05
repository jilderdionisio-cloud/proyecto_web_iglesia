from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from members.models import Member
from .models import Donation


class DonationApiTests(APITestCase):
    def setUp(self):
        self.treasurer = User.objects.create_user(email='tesorera@iglesia.test', password='ClaveSegura123!', role=User.Role.TREASURER)
        self.member = Member.objects.create(first_name='Ana', last_name='Pérez')
        self.client.force_authenticate(self.treasurer)

    def donate(self, **extra):
        return self.client.post('/api/donations/', {'amount': '100.50', 'date': '2026-10-05', 'member': self.member.pk, **extra}, format='json')

    def test_create_with_member(self):
        create = self.donate(donation_type='tithe')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data['donor'], 'Ana Pérez')
        self.assertEqual(create.data['type_label'], 'Diezmo')
        self.assertEqual(Donation.objects.get().registered_by, self.treasurer)

    def test_anonymous_donation_does_not_store_identity(self):
        create = self.donate(is_anonymous=True, donor_name='Ana')
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create.data['donor'], 'Anónimo')
        donation = Donation.objects.get()
        self.assertIsNone(donation.member)
        self.assertEqual(donation.donor_name, '')

    def test_marking_as_anonymous_later_erases_identity(self):
        donation_id = self.donate().data['id']
        update = self.client.patch(f'/api/donations/{donation_id}/', {'is_anonymous': True}, format='json')
        self.assertEqual(update.data['donor'], 'Anónimo')
        self.assertIsNone(Donation.objects.get().member)

    def test_database_rejects_anonymous_with_donor(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Donation.objects.create(amount='5', date='2026-10-05', is_anonymous=True, member=self.member, registered_by=self.treasurer)

    def test_external_donor_is_accepted(self):
        create = self.client.post('/api/donations/', {'amount': '50', 'date': '2026-10-05', 'donor_name': 'Empresa X'}, format='json')
        self.assertEqual(create.data['donor'], 'Empresa X')

    def test_invalid_donations_are_rejected(self):
        self.assertEqual(self.client.post('/api/donations/', {'amount': '50', 'date': '2026-10-05'}, format='json').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.donate(amount='0').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.donate(amount='-10').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.donate(amount='abc').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.donate(donation_type='rifa').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.donate(member=99999).status_code, status.HTTP_400_BAD_REQUEST)

    def test_filters_and_summary(self):
        self.donate(donation_type='tithe', amount='100.00', date='2026-09-10')
        self.donate(donation_type='offering', amount='50.00', date='2026-10-10')
        self.donate(donation_type='offering', amount='25.00', date='2026-10-20', is_anonymous=True)
        self.assertEqual(len(self.client.get('/api/donations/?from=2026-10-01&to=2026-10-31').data), 2)
        self.assertEqual(len(self.client.get('/api/donations/?type=tithe').data), 1)
        self.assertEqual(len(self.client.get('/api/donations/?anonymous=true').data), 1)
        self.assertEqual(len(self.client.get(f'/api/donations/?member={self.member.pk}').data), 2)
        self.assertEqual(self.client.get('/api/donations/?from=ayer').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get('/api/donations/?page=1&page_size=2').data['count'], 3)

        summary = self.client.get('/api/donations/summary/').data
        self.assertEqual(summary['total'], 175)
        self.assertEqual(summary['count'], 3)
        self.assertEqual(summary['anonymous_total'], 25)
        self.assertEqual(summary['by_type'][0]['label'], 'Diezmo')
        self.assertEqual(summary['by_month'], [{'month': '2026-09', 'total': 100}, {'month': '2026-10', 'total': 75}])
        self.assertEqual(self.client.get('/api/donations/summary/?from=2026-10-01').data['total'], 75)

    def test_financial_permissions(self):
        donation_id = self.donate().data['id']
        for role, summary_status in ((User.Role.PASTOR, status.HTTP_200_OK), (User.Role.SECRETARY, status.HTTP_403_FORBIDDEN), (User.Role.COORDINATOR, status.HTTP_403_FORBIDDEN)):
            self.client.force_authenticate(User.objects.create_user(email=f'{role}@iglesia.test', password='ClaveSegura123!', role=role))
            self.assertEqual(self.client.get('/api/donations/summary/').status_code, summary_status)
            self.assertEqual(self.client.get('/api/donations/').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.get(f'/api/donations/{donation_id}/').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.donate().status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.delete(f'/api/donations/{donation_id}/').status_code, status.HTTP_403_FORBIDDEN)

    def test_administrator_manages_finances(self):
        self.client.force_authenticate(User.objects.create_user(email='admin@iglesia.test', password='ClaveSegura123!', role=User.Role.ADMINISTRATOR))
        self.assertEqual(self.donate().status_code, status.HTTP_201_CREATED)
