from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import CanManageAnnouncements
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = (CanManageAnnouncements,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'body')

    def get_queryset(self):
        queryset = Announcement.objects.select_related('author')
        user = self.request.user
        can_manage = user.is_superuser or user.role in CanManageAnnouncements.allowed_roles
        if can_manage and self.request.query_params.get('visible') != 'true':
            return queryset
        return queryset.visible()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('post',))
    def publish(self, request, pk=None):
        announcement = self.get_object()
        if announcement.expires_at and announcement.expires_at <= timezone.now():
            return Response({'detail': 'Actualiza la vigencia antes de publicar este comunicado.'}, status=status.HTTP_400_BAD_REQUEST)
        announcement.is_published = True
        announcement.published_at = timezone.now()
        announcement.save(update_fields=('is_published', 'published_at', 'updated_at'))
        return Response(self.get_serializer(announcement).data)

    @action(detail=True, methods=('post',))
    def unpublish(self, request, pk=None):
        announcement = self.get_object()
        announcement.is_published = False
        announcement.save(update_fields=('is_published', 'updated_at'))
        return Response(self.get_serializer(announcement).data)
