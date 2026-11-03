import io
from django.http import FileResponse
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from accounts.permissions import HasRole, CanManageFinances
from members.models import Member
from events.models import Event
from ministries.models import Ministry
from attendance.models import AttendanceRecord
from finance.models import Donation

class OperationalAccess(HasRole): allowed_roles=(User.Role.ADMINISTRATOR,User.Role.PASTOR,User.Role.SECRETARY,User.Role.COORDINATOR)
class DashboardView(APIView):
    permission_classes=(OperationalAccess,)
    def get(self,request):
        data={'active_members':Member.objects.filter(is_active=True).count(),'upcoming_events':Event.objects.filter(starts_at__gte=timezone.now(),status='scheduled').count(),'ministries':Ministry.objects.filter(is_active=True).count(),'attendance':AttendanceRecord.objects.values('status').annotate(count=Count('id'))}
        if request.user.is_superuser or request.user.role in (User.Role.ADMINISTRATOR,User.Role.TREASURER): data['income']=Donation.objects.aggregate(total=Sum('amount'))['total'] or 0
        return Response(data)
class ReportView(APIView):
    permission_classes=(OperationalAccess,)
    def get(self,request,kind,format):
        if kind=='members': rows=[['Nombre','Correo','Activo']]+[[str(x),x.email,'Sí' if x.is_active else 'No'] for x in Member.objects.all()]
        elif kind=='attendance': rows=[['Miembro','Estado']]+[[str(x.member),x.status] for x in AttendanceRecord.objects.select_related('member')]
        elif kind=='ministries': rows=[['Ministerio','Integrantes']]+[[x.name,x.members.count()] for x in Ministry.objects.all()]
        elif kind=='income':
            if not (request.user.is_superuser or request.user.role in (User.Role.ADMINISTRATOR,User.Role.TREASURER)): return Response({'detail':'Sin permiso financiero.'},status=403)
            rows=[['Fecha','Monto','Concepto']]+[[str(x.received_at),str(x.amount),x.concept] for x in Donation.objects.all()]
        else: return Response({'detail':'Reporte no válido.'},status=404)
        if format=='xlsx':
            import xlsxwriter
            output=io.BytesIO(); wb=xlsxwriter.Workbook(output,{'in_memory':True}); ws=wb.add_worksheet('Reporte')
            for r,row in enumerate(rows):
                for c,value in enumerate(row): ws.write(r,c,value)
            wb.close(); output.seek(0); return FileResponse(output,as_attachment=True,filename=f'{kind}.xlsx')
        from reportlab.pdfgen import canvas
        output=io.BytesIO(); pdf=canvas.Canvas(output); y=800
        for row in rows:
            pdf.drawString(40,y,' | '.join(map(str,row))[:120]); y-=18
            if y<50: pdf.showPage(); y=800
        pdf.save(); output.seek(0); return FileResponse(output,as_attachment=True,filename=f'{kind}.pdf')
