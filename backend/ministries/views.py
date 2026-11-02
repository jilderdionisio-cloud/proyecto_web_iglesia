from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import HasRole
from .models import Ministry, MinistryMembership
from .serializers import MemberAssignmentSerializer, MinistrySerializer


class CanManageMinistries(HasRole):
    allowed_roles = (User.Role.ADMINISTRATOR, User.Role.PASTOR, User.Role.SECRETARY, User.Role.COORDINATOR)


class MinistryViewSet(viewsets.ModelViewSet):
    serializer_class = MinistrySerializer
    permission_classes = (CanManageMinistries,)

    def get_queryset(self):
        queryset = Ministry.objects.select_related('coordinator').prefetch_related('memberships__member')
        active = self.request.query_params.get('active')
        if active in ('true', 'false'):
            queryset = queryset.filter(is_active=active == 'true')
        return queryset

    @action(detail=True, methods=('post', 'delete'), url_path='members')
    def members(self, request, pk=None):
        ministry = self.get_object()
        serializer = MemberAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        member = serializer.validated_data['member']
        if request.method == 'POST':
            MinistryMembership.objects.get_or_create(ministry=ministry, member=member)
            return Response(self.get_serializer(self.get_queryset().get(pk=ministry.pk)).data, status=status.HTTP_200_OK)
        deleted, _ = MinistryMembership.objects.filter(ministry=ministry, member=member).delete()
        if not deleted:
            return Response({'detail': 'El miembro no pertenece a este ministerio.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
