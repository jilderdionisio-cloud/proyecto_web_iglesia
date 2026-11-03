from datetime import timedelta

from django.db import transaction
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import HasRole
from members.models import Member
from .models import AttendanceRecord, AttendanceSession
from .serializers import AttendanceBulkUpdateSerializer, AttendanceRecordSerializer, AttendanceSessionSerializer


class CanManageAttendance(HasRole):
    allowed_roles = (User.Role.ADMINISTRATOR, User.Role.SECRETARY)


class AttendanceSessionViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSessionSerializer
    permission_classes = (CanManageAttendance,)
    http_method_names = ('get', 'post', 'put', 'head', 'options')

    def get_queryset(self):
        queryset = AttendanceSession.objects.select_related('event').prefetch_related('records__member')
        event = self.request.query_params.get('event')
        date = self.request.query_params.get('date')
        if event:
            queryset = queryset.filter(event_id=event)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    def perform_create(self, serializer):
        with transaction.atomic():
            session = serializer.save(created_by=self.request.user)
            AttendanceRecord.objects.bulk_create([
                AttendanceRecord(session=session, member=member, marked_by=self.request.user)
                for member in Member.objects.filter(is_active=True)
            ])

    @action(detail=True, methods=('put',), url_path='records')
    def update_records(self, request, pk=None):
        session = self.get_object()
        serializer = AttendanceBulkUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        members = {member.pk: member for member in Member.objects.filter(pk__in=[item['member'] for item in serializer.validated_data['records']])}
        if len(members) != len({item['member'] for item in serializer.validated_data['records']}):
            return Response({'detail': 'Uno o más miembros no existen.'}, status=status.HTTP_400_BAD_REQUEST)
        with transaction.atomic():
            for item in serializer.validated_data['records']:
                AttendanceRecord.objects.update_or_create(
                    session=session, member=members[item['member']],
                    defaults={'status': item['status'], 'marked_by': request.user},
                )
        session = self.get_queryset().get(pk=session.pk)
        return Response(self.get_serializer(session).data)


class AttendanceHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AttendanceRecordSerializer
    permission_classes = (CanManageAttendance,)

    def get_queryset(self):
        queryset = AttendanceRecord.objects.select_related('member', 'session__event')
        event = self.request.query_params.get('event')
        date = self.request.query_params.get('date')
        member = self.request.query_params.get('member')
        if event:
            queryset = queryset.filter(session__event_id=event)
        if date:
            queryset = queryset.filter(session__date=date)
        if member:
            queryset = queryset.filter(member_id=member)
        return queryset

    @action(detail=False, methods=('get',))
    def summary(self, request):
        period = request.query_params.get('period', 'week')
        if period not in ('week', 'month'):
            return Response({'detail': 'period debe ser week o month.'}, status=status.HTTP_400_BAD_REQUEST)
        reference = request.query_params.get('date')
        end = timezone.datetime.fromisoformat(reference).date() if reference else timezone.localdate()
        start = end - timedelta(days=6 if period == 'week' else 29)
        totals = self.get_queryset().filter(session__date__range=(start, end)).aggregate(
            present=Count('id', filter=Q(status=AttendanceRecord.Status.PRESENT)),
            absent=Count('id', filter=Q(status=AttendanceRecord.Status.ABSENT)),
        )
        return Response({'period': period, 'from': start, 'to': end, **totals})
