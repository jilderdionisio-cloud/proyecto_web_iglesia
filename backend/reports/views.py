from django.http import Http404, HttpResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import CanManageFinances, CanViewOperationalReports
from church.models import ChurchProfile
from core.params import date_range
from .exporters import to_pdf, to_xlsx
from .services import (
    attendance_report, dashboard_data, donations_report, events_report, members_report, ministries_report,
)

REPORTS = {
    'members': (members_report, CanViewOperationalReports),
    'attendance': (attendance_report, CanViewOperationalReports),
    'events': (events_report, CanViewOperationalReports),
    'ministries': (ministries_report, CanViewOperationalReports),
    'donations': (donations_report, CanManageFinances),
}
EXPORTS = {
    'xlsx': (to_xlsx, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'pdf': (to_pdf, 'application/pdf'),
}


class ReportView(APIView):
    def get_permissions(self):
        if self.kwargs['report'] not in REPORTS:
            raise Http404
        return [REPORTS[self.kwargs['report']][1]()]

    def get(self, request, report):
        start, end = date_range(request)
        data = REPORTS[report][0](start, end)
        export = request.query_params.get('export')
        if not export:
            return Response(data)
        if export not in EXPORTS:
            return Response({'detail': 'export debe ser pdf o xlsx.'}, status=400)
        render, content_type = EXPORTS[export]
        response = HttpResponse(render(data, ChurchProfile.load().name, start, end), content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="reporte-{report}-{timezone.localdate().isoformat()}.{export}"'
        return response


class DashboardView(APIView):
    def get(self, request):
        return Response(dashboard_data(request.user))
