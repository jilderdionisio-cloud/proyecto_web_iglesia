from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import CanManageFinances, CanViewFinancialSummary
from core.pagination import OptionalPageNumberPagination
from core.params import date_range, int_param
from .models import Donation
from .serializers import DonationSerializer


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    permission_classes = (CanManageFinances,)
    pagination_class = OptionalPageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('donor_name', 'member__first_name', 'member__last_name', 'notes')

    def get_permissions(self):
        # Quien solo consulta totales no ve donaciones individuales ni a sus donantes.
        if self.action == 'summary':
            return [CanViewFinancialSummary()]
        return super().get_permissions()

    def filter_by_period_and_type(self):
        queryset = Donation.objects.select_related('member')
        start, end = date_range(self.request)
        donation_type = self.request.query_params.get('type')
        if start:
            queryset = queryset.filter(date__gte=start)
        if end:
            queryset = queryset.filter(date__lte=end)
        if donation_type in Donation.Type.values:
            queryset = queryset.filter(donation_type=donation_type)
        return queryset

    def get_queryset(self):
        queryset = self.filter_by_period_and_type()
        member = int_param(self.request, 'member')
        anonymous = self.request.query_params.get('anonymous')
        if member:
            queryset = queryset.filter(member_id=member)
        if anonymous in ('true', 'false'):
            queryset = queryset.filter(is_anonymous=anonymous == 'true')
        return queryset

    def perform_create(self, serializer):
        serializer.save(registered_by=self.request.user)

    @action(detail=False, methods=('get',))
    def summary(self, request):
        queryset = self.filter_by_period_and_type().order_by()
        totals = queryset.aggregate(total=Sum('amount'), count=Count('id'))
        anonymous_total = queryset.filter(is_anonymous=True).aggregate(total=Sum('amount'))['total']
        labels = dict(Donation.Type.choices)
        by_type = queryset.values('donation_type').annotate(total=Sum('amount'), count=Count('id')).order_by('-total')
        by_month = queryset.annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')
        return Response({
            'total': totals['total'] or 0,
            'count': totals['count'],
            'anonymous_total': anonymous_total or 0,
            'by_type': [{'type': row['donation_type'], 'label': labels[row['donation_type']], 'total': row['total'], 'count': row['count']} for row in by_type],
            'by_month': [{'month': row['month'].strftime('%Y-%m'), 'total': row['total']} for row in by_month],
        })
