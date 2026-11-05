from rest_framework import permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import CanManageChurch
from .models import ChurchProfile, ServiceSchedule
from .serializers import ChurchProfileSerializer, ServiceScheduleSerializer


class ChurchProfileView(APIView):
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_permissions(self):
        # Nombre, logo, contacto y horarios son públicos: también se muestran en el inicio de sesión.
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [CanManageChurch()]

    def get(self, request):
        return Response(ChurchProfileSerializer(ChurchProfile.load()).data)

    def patch(self, request):
        serializer = ChurchProfileSerializer(ChurchProfile.load(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ServiceScheduleViewSet(viewsets.ModelViewSet):
    queryset = ServiceSchedule.objects.all()
    serializer_class = ServiceScheduleSerializer
    permission_classes = (CanManageChurch,)
