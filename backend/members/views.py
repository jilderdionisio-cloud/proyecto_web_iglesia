from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import HasRole

from .models import Member
from .serializers import MemberSerializer


class CanManageMembers(HasRole):
    allowed_roles = (User.Role.ADMINISTRATOR, User.Role.PASTOR, User.Role.SECRETARY, User.Role.COORDINATOR)


class MemberViewSet(viewsets.ModelViewSet):
    serializer_class = MemberSerializer
    permission_classes = (IsAuthenticated, CanManageMembers)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    ordering_fields = ('first_name', 'last_name', 'joined_at', 'created_at')

    def get_queryset(self):
        queryset = Member.objects.all()
        active = self.request.query_params.get('active')
        if active in ('true', 'false'):
            queryset = queryset.filter(is_active=active == 'true')
        return queryset

    def destroy(self, request, *args, **kwargs):
        member = self.get_object()
        member.is_active = False
        member.save(update_fields=('is_active', 'updated_at'))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=('post',))
    def activate(self, request, pk=None):
        member = self.get_object()
        member.is_active = True
        member.save(update_fields=('is_active', 'updated_at'))
        return Response(self.get_serializer(member).data)
