from django.db.models import Sum
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.permissions import CanManageFinances
from .models import Donation
from .serializers import DonationSerializer

class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = (CanManageFinances,)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('concept','donor_name')
    ordering_fields = ('received_at','amount')
    def get_queryset(self):
        qs = Donation.objects.all()
        start, end = self.request.query_params.get('start'), self.request.query_params.get('end')
        if start: qs = qs.filter(received_at__gte=start)
        if end: qs = qs.filter(received_at__lte=end)
        return qs
    def perform_create(self, serializer): serializer.save(registered_by=self.request.user)
    @action(detail=False, methods=('get',))
    def summary(self, request):
        qs = self.get_queryset()
        return Response({'total': qs.aggregate(total=Sum('amount'))['total'] or 0, 'count': qs.count()})
