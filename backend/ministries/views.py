from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from accounts.permissions import CanManageMinistries, CanManageMinistryActivities, is_scoped_coordinator
from core.params import date_range, int_param
from .models import Ministry, MinistryActivity, MinistryMembership
from .serializers import MemberAssignmentSerializer, MinistryActivitySerializer, MinistrySerializer


class MinistryViewSet(viewsets.ModelViewSet):
    serializer_class = MinistrySerializer
    permission_classes = (CanManageMinistries,)

    def get_queryset(self):
        queryset = Ministry.objects.select_related('coordinator').prefetch_related('memberships__member')
        active = self.request.query_params.get('active')
        if active in ('true', 'false'):
            queryset = queryset.filter(is_active=active == 'true')
        return queryset

    def perform_update(self, serializer):
        if is_scoped_coordinator(self.request.user):
            serializer.save(coordinator=self.request.user)
        else:
            serializer.save()

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


class MinistryActivityViewSet(viewsets.ModelViewSet):
    serializer_class = MinistryActivitySerializer
    permission_classes = (CanManageMinistryActivities,)

    def get_queryset(self):
        queryset = MinistryActivity.objects.select_related('ministry')
        ministry = int_param(self.request, 'ministry')
        start, end = date_range(self.request)
        if ministry:
            queryset = queryset.filter(ministry_id=ministry)
        if start:
            queryset = queryset.filter(date__gte=start)
        if end:
            queryset = queryset.filter(date__lte=end)
        return queryset

    def perform_create(self, serializer):
        ministry = serializer.validated_data['ministry']
        if is_scoped_coordinator(self.request.user) and ministry.coordinator_id != self.request.user.id:
            raise PermissionDenied('Solo puedes registrar actividades en los ministerios que coordinas.')
        serializer.save(created_by=self.request.user)
