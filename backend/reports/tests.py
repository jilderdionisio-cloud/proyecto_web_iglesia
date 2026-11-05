from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.utils import timezone
from openpyxl import load_workbook
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import User
from announcements.models import Announcement
from attendance.models import AttendanceRecord, AttendanceSession
from church.models import ChurchProfile
from donations.models import Donation
from events.models import Event
from members.models import Member
from ministries.models import Ministry, MinistryActivity, MinistryMembership
from .services import financial_summary, month_start, weekly_attendance


def user_with(role):
    return User.objects.create_user(email=f'{role}@iglesia.test', password='ClaveSegura123!', role=role)


class ReportTestData(APITestCase):
    def setUp(self):
        self.admin = user_with(User.Role.ADMINISTRATOR)
        self.today = timezone.localdate()
        self.member = Member.objects.create(first_name='Ana', last_name='<Pérez>', email='=1+1')
        self.other = Member.objects.create(first_name='Luis', last_name='Díaz', is_active=False)
        self.event = Event.objects.create(title='Culto', starts_at=timezone.now() + timedelta(days=1), location='Templo', responsible=self.admin)
        session = AttendanceSession.objects.create(event=self.event, date=self.today, created_by=self.admin)
        AttendanceRecord.objects.create(session=session, member=self.member, status=AttendanceRecord.Status.PRESENT, marked_by=self.admin)
        AttendanceRecord.objects.create(session=session, member=self.other, marked_by=self.admin)
        self.ministry = Ministry.objects.create(name='Alabanza', coordinator=self.admin)
        MinistryMembership.objects.create(ministry=self.ministry, member=self.member)
        MinistryActivity.objects.create(ministry=self.ministry, title='Ensayo', date=self.today, created_by=self.admin)
        Donation.objects.create(amount=Decimal('100.50'), date=self.today, member=self.member, registered_by=self.admin)
        Donation.objects.create(amount=Decimal('20.00'), date=self.today, is_anonymous=True, registered_by=self.admin)
        self.client.force_authenticate(self.admin)


class ReportApiTests(ReportTestData):
    def test_reports_return_rows_and_totals(self):
        members = self.client.get('/api/reports/members/').data
        self.assertEqual(len(members['rows']), 2)
        self.assertIn(['Activos', 1], members['totals'])
        attendance = self.client.get('/api/reports/attendance/').data
        self.assertEqual(attendance['rows'][0][1:], ['Culto', 1, 1, 50.0])
        events = self.client.get('/api/reports/events/').data
        self.assertEqual(events['rows'][0][1], 'Culto')
        ministries = self.client.get('/api/reports/ministries/').data
        self.assertEqual(ministries['rows'][0][2:4], [1, 1])
        donations = self.client.get('/api/reports/donations/').data
        self.assertEqual(donations['totals'][1][1], Decimal('120.50'))
        self.assertIn('Anónimo', [row[3] for row in donations['rows']])

    def test_reports_filter_by_period(self):
        tomorrow = (self.today + timedelta(days=1)).isoformat()
        self.assertEqual(self.client.get(f'/api/reports/attendance/?from={tomorrow}').data['rows'], [])
        self.assertEqual(self.client.get(f'/api/reports/donations/?from={tomorrow}').data['rows'], [])
        self.assertEqual(self.client.get(f'/api/reports/ministries/?from={tomorrow}').data['rows'][0][3], 0)

    def test_invalid_requests(self):
        self.assertEqual(self.client.get('/api/reports/inexistente/').status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get('/api/reports/members/?from=ayer').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get('/api/reports/members/?export=docx').status_code, status.HTTP_400_BAD_REQUEST)

    def test_every_report_exports_to_pdf_and_excel(self):
        for report in ('members', 'attendance', 'events', 'ministries', 'donations'):
            pdf = self.client.get(f'/api/reports/{report}/?export=pdf')
            self.assertEqual(pdf.status_code, status.HTTP_200_OK, report)
            self.assertEqual(pdf['Content-Type'], 'application/pdf')
            self.assertTrue(pdf.content.startswith(b'%PDF'))
            excel = self.client.get(f'/api/reports/{report}/?export=xlsx')
            self.assertEqual(excel.status_code, status.HTTP_200_OK, report)
            self.assertIn(f'reporte-{report}-', excel['Content-Disposition'])
            self.assertTrue(load_workbook(BytesIO(excel.content)).active.max_row > 5)

    def test_excel_treats_user_text_as_text(self):
        ChurchProfile.objects.update_or_create(pk=1, defaults={'name': 'Iglesia Central'})
        excel = self.client.get('/api/reports/members/?export=xlsx')
        sheet = load_workbook(BytesIO(excel.content)).active
        self.assertEqual(sheet['A1'].value, 'Iglesia Central')
        cell = next(cell for row in sheet.iter_rows() for cell in row if cell.value == '=1+1')
        self.assertEqual(cell.data_type, 's')

    def test_operational_report_permissions(self):
        for role in (User.Role.PASTOR, User.Role.SECRETARY):
            self.client.force_authenticate(user_with(role))
            self.assertEqual(self.client.get('/api/reports/members/').status_code, status.HTTP_200_OK)
            self.assertEqual(self.client.get('/api/reports/donations/').status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(self.client.get('/api/reports/donations/?export=pdf').status_code, status.HTTP_403_FORBIDDEN)

    def test_treasurer_only_gets_financial_report(self):
        self.client.force_authenticate(user_with(User.Role.TREASURER))
        self.assertEqual(self.client.get('/api/reports/donations/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/reports/members/').status_code, status.HTTP_403_FORBIDDEN)

    def test_coordinator_has_no_reports(self):
        self.client.force_authenticate(user_with(User.Role.COORDINATOR))
        self.assertEqual(self.client.get('/api/reports/attendance/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get('/api/reports/donations/').status_code, status.HTTP_403_FORBIDDEN)

    def test_reports_require_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/reports/members/').status_code, status.HTTP_401_UNAUTHORIZED)


class DashboardApiTests(ReportTestData):
    def test_metrics(self):
        Announcement.objects.create(title='Aviso', body='x', author=self.admin, is_published=True, published_at=timezone.now())
        Announcement.objects.create(title='Borrador', body='x', author=self.admin)
        data = self.client.get('/api/dashboard/').data
        self.assertEqual(data['metrics']['active_members'], 1)
        self.assertEqual(data['metrics']['upcoming_events'], 1)
        self.assertEqual(data['metrics']['active_ministries'], 1)
        self.assertEqual(data['metrics']['weekly_attendance'], {'present': 1, 'absent': 1, 'rate': 50.0})
        self.assertEqual([item['title'] for item in data['announcements']], ['Aviso'])
        self.assertEqual(data['upcoming_events'][0]['title'], 'Culto')
        self.assertEqual(len(data['attendance_trend']), 8)
        self.assertEqual(data['attendance_trend'][-1]['present'], 1)
        self.assertEqual(data['finances']['month_total'], Decimal('120.50'))

    def test_financial_data_is_restricted(self):
        for role, visible in ((User.Role.PASTOR, True), (User.Role.TREASURER, True), (User.Role.SECRETARY, False), (User.Role.COORDINATOR, False)):
            self.client.force_authenticate(user_with(role))
            finances = self.client.get('/api/dashboard/').data['finances']
            self.assertEqual(finances is not None, visible, role)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/dashboard/').status_code, status.HTTP_401_UNAUTHORIZED)


class HelperTests(ReportTestData):
    def test_month_start_crosses_year_boundary(self):
        self.assertEqual(month_start(date(2026, 1, 31), 1), date(2025, 12, 1))
        self.assertEqual(month_start(date(2026, 3, 31), 1), date(2026, 2, 1))
        self.assertEqual(month_start(date(2026, 11, 2), 12), date(2025, 11, 1))

    def test_financial_comparison(self):
        previous = month_start(self.today, 1)
        Donation.objects.create(amount=Decimal('60.25'), date=previous, is_anonymous=True, registered_by=self.admin)
        summary = financial_summary(self.today)
        self.assertEqual(summary['previous_month_total'], Decimal('60.25'))
        self.assertEqual(summary['change_percent'], Decimal('100.0'))
        self.assertEqual(len(summary['monthly']), 6)

    def test_financial_comparison_without_previous_month(self):
        self.assertIsNone(financial_summary(self.today)['change_percent'])

    def test_weekly_attendance_fills_empty_weeks(self):
        series = weekly_attendance(self.today, weeks=4)
        self.assertEqual([week['present'] for week in series], [0, 0, 0, 1])
        self.assertEqual(series[-1]['week'].weekday(), 0)
