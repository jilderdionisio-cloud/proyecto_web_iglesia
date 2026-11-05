from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone

from accounts.permissions import CanViewFinancialSummary
from announcements.models import Announcement
from attendance.models import AttendanceRecord, AttendanceSession
from finance.models import Donation
from events.models import Event
from members.models import Member
from ministries.models import Ministry


def between(queryset, field, start, end):
    if start:
        queryset = queryset.filter(**{f'{field}__gte': start})
    if end:
        queryset = queryset.filter(**{f'{field}__lte': end})
    return queryset


def attendance_rate(present, absent):
    total = present + absent
    return round(present * 100 / total, 1) if total else 0


def members_report(start, end):
    members = between(Member.objects.prefetch_related('ministries'), 'joined_at', start, end)
    rows = [
        [str(member), member.email, member.phone, member.joined_at.isoformat(), 'Activo' if member.is_active else 'Inactivo', ', '.join(ministry.name for ministry in member.ministries.all())]
        for member in members
    ]
    return {
        'title': 'Reporte de miembros',
        'columns': ['Nombre', 'Correo', 'Teléfono', 'Registro', 'Estado', 'Ministerios'],
        'rows': rows,
        'totals': [['Miembros', len(rows)], ['Activos', sum(row[4] == 'Activo' for row in rows)]],
    }


def attendance_report(start, end):
    present = Count('records', filter=Q(records__status=AttendanceRecord.Status.PRESENT))
    absent = Count('records', filter=Q(records__status=AttendanceRecord.Status.ABSENT))
    sessions = between(AttendanceSession.objects.select_related('event'), 'date', start, end).annotate(present=present, absent=absent)
    rows = [
        [session.date.isoformat(), session.event.title, session.present, session.absent, attendance_rate(session.present, session.absent)]
        for session in sessions
    ]
    total_present, total_absent = sum(row[2] for row in rows), sum(row[3] for row in rows)
    return {
        'title': 'Reporte de asistencia',
        'columns': ['Fecha', 'Evento', 'Presentes', 'Ausentes', 'Asistencia %'],
        'rows': rows,
        'totals': [['Listas', len(rows)], ['Presentes', total_present], ['Ausentes', total_absent], ['Asistencia %', attendance_rate(total_present, total_absent)]],
    }


def events_report(start, end):
    events = between(Event.objects.select_related('responsible'), 'starts_at__date', start, end)
    rows = [
        [timezone.localtime(event.starts_at).strftime('%Y-%m-%d %H:%M'), event.title, event.location, event.responsible.get_full_name() or event.responsible.email, event.get_status_display()]
        for event in events
    ]
    return {
        'title': 'Reporte de eventos',
        'columns': ['Inicio', 'Evento', 'Lugar', 'Responsable', 'Estado'],
        'rows': rows,
        'totals': [['Eventos', len(rows)], ['Cancelados', sum(row[4] == Event.Status.CANCELLED.label for row in rows)]],
    }


def ministries_report(start, end):
    activities = Q()
    if start:
        activities &= Q(activities__date__gte=start)
    if end:
        activities &= Q(activities__date__lte=end)
    ministries = Ministry.objects.select_related('coordinator').annotate(
        member_total=Count('memberships', distinct=True),
        activity_total=Count('activities', filter=activities, distinct=True),
    )
    rows = [
        [ministry.name, ministry.coordinator.get_full_name() or ministry.coordinator.email, ministry.member_total, ministry.activity_total, 'Activo' if ministry.is_active else 'Inactivo']
        for ministry in ministries
    ]
    return {
        'title': 'Reporte de ministerios',
        'columns': ['Ministerio', 'Coordinador', 'Integrantes', 'Actividades', 'Estado'],
        'rows': rows,
        'totals': [['Ministerios', len(rows)], ['Actividades', sum(row[3] for row in rows)]],
    }


def donations_report(start, end):
    donations = between(Donation.objects.select_related('member'), 'date', start, end)
    rows = [
        [donation.date.isoformat(), donation.get_donation_type_display(), donation.get_payment_method_display(), donation.donor, donation.amount]
        for donation in donations
    ]
    return {
        'title': 'Reporte de donaciones',
        'columns': ['Fecha', 'Tipo', 'Método', 'Donante', 'Importe'],
        'rows': rows,
        'totals': [['Donaciones', len(rows)], ['Total', sum((row[4] for row in rows), Decimal('0'))]],
    }


def weekly_attendance(today, weeks=8):
    first = today - timedelta(days=today.weekday(), weeks=weeks - 1)
    rows = (
        AttendanceRecord.objects.filter(session__date__range=(first, today))
        .annotate(week=TruncWeek('session__date')).values('week')
        .annotate(
            present=Count('id', filter=Q(status=AttendanceRecord.Status.PRESENT)),
            absent=Count('id', filter=Q(status=AttendanceRecord.Status.ABSENT)),
        ).order_by('week')
    )
    totals = {row['week']: row for row in rows}
    series = []
    for offset in range(weeks):
        week = first + timedelta(weeks=offset)
        row = totals.get(week, {})
        series.append({'week': week, 'present': row.get('present', 0), 'absent': row.get('absent', 0)})
    return series


def month_start(today, months_back):
    index = today.year * 12 + today.month - 1 - months_back
    return today.replace(year=index // 12, month=index % 12 + 1, day=1)


def financial_summary(today, months=6):
    first = month_start(today, months - 1)
    rows = Donation.objects.filter(date__range=(first, today)).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
    totals = {row['month']: row['total'] for row in rows}
    monthly = []
    for back in range(months - 1, -1, -1):
        month = month_start(today, back)
        monthly.append({'month': month.strftime('%Y-%m'), 'total': totals.get(month, Decimal('0'))})
    current, previous = monthly[-1]['total'], monthly[-2]['total']
    return {
        'month_total': current,
        'previous_month_total': previous,
        'change_percent': round((current - previous) * 100 / previous, 1) if previous else None,
        'monthly': monthly,
    }


def can_view_finances(user):
    return user.is_superuser or user.role in CanViewFinancialSummary.allowed_roles


def dashboard_data(user):
    today = timezone.localdate()
    upcoming = Event.objects.select_related('responsible').filter(starts_at__gte=timezone.now(), status=Event.Status.SCHEDULED)
    week = AttendanceRecord.objects.filter(session__date__range=(today - timedelta(days=6), today)).aggregate(
        present=Count('id', filter=Q(status=AttendanceRecord.Status.PRESENT)),
        absent=Count('id', filter=Q(status=AttendanceRecord.Status.ABSENT)),
    )
    return {
        'metrics': {
            'active_members': Member.objects.filter(is_active=True).count(),
            'upcoming_events': upcoming.count(),
            'active_ministries': Ministry.objects.filter(is_active=True).count(),
            'weekly_attendance': {**week, 'rate': attendance_rate(week['present'], week['absent'])},
        },
        'upcoming_events': [
            {'id': event.id, 'title': event.title, 'starts_at': event.starts_at, 'location': event.location}
            for event in upcoming[:5]
        ],
        'announcements': [
            {'id': item.id, 'title': item.title, 'body': item.body, 'published_at': item.published_at}
            for item in Announcement.objects.visible()[:3]
        ],
        'attendance_trend': weekly_attendance(today),
        'finances': financial_summary(today) if can_view_finances(user) else None,
    }
