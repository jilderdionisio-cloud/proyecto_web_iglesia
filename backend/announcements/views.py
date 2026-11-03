from rest_framework import viewsets
from accounts.models import User
from accounts.permissions import HasRole
from .models import Announcement
from .serializers import AnnouncementSerializer
class CanManageAnnouncements(HasRole): allowed_roles=(User.Role.ADMINISTRATOR,User.Role.PASTOR,User.Role.SECRETARY)
class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class=AnnouncementSerializer; permission_classes=(CanManageAnnouncements,)
    def get_queryset(self): return Announcement.objects.all()
    def perform_create(self, serializer): serializer.save(author=self.request.user)
