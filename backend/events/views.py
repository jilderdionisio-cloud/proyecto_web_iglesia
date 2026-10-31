from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import HasRole

from .models import Event
from .serializers import EventSerializer


class CanManageEvents(HasRole):
    allowed_roles = (User.Role.ADMINISTRATOR, User.Role.PASTOR, User.Role.SECRETARY, User.Role.COORDINATOR)


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
        return queryset

    def perform_create(self, serializer):
        serializer.save(responsible=self.request.user)

    @action(detail=True, methods=('post',))
    def cancel(self, request, pk=None):
        event = self.get_object()
        reason = request.data.get('reason', '').strip()
        event.status = Event.Status.CANCELLED
        event.cancellation_reason = reason
        event.save(update_fields=('status', 'cancellation_reason', 'updated_at'))
        return Response(self.get_serializer(event).data, status=status.HTTP_200_OK)
