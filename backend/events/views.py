from django.db.models import ProtectedError
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import CanManageEvents, is_scoped_coordinator
from core.params import date_range

from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = (CanManageEvents,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('title', 'location', 'description')
    ordering_fields = ('starts_at', 'title', 'created_at')

    def get_queryset(self):
        queryset = Event.objects.select_related('responsible').all()
        status_filter = self.request.query_params.get('status')
        if status_filter in Event.Status.values:
            queryset = queryset.filter(status=status_filter)
        upcoming = self.request.query_params.get('upcoming')
        if upcoming == 'true':
            queryset = queryset.filter(starts_at__gte=timezone.now(), status=Event.Status.SCHEDULED)
        start, end = date_range(self.request)
        if start:
            queryset = queryset.filter(starts_at__date__gte=start)
        if end:
            queryset = queryset.filter(starts_at__date__lte=end)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        responsible = user if is_scoped_coordinator(user) else serializer.validated_data.get('responsible', user)
        serializer.save(responsible=responsible)

    def perform_update(self, serializer):
        if is_scoped_coordinator(self.request.user):
            serializer.save(responsible=self.request.user)
        else:
            serializer.save()

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({'detail': 'El evento tiene asistencias registradas; cancélalo en lugar de eliminarlo.'}, status=status.HTTP_409_CONFLICT)

    @action(detail=True, methods=('post',))
    def cancel(self, request, pk=None):
        event = self.get_object()
        if event.status == Event.Status.CANCELLED:
            return Response({'detail': 'El evento ya está cancelado.'}, status=status.HTTP_400_BAD_REQUEST)
        reason = request.data.get('reason', '').strip()
        event.status = Event.Status.CANCELLED
        event.cancellation_reason = reason
        event.save(update_fields=('status', 'cancellation_reason', 'updated_at'))
        return Response(self.get_serializer(event).data, status=status.HTTP_200_OK)
