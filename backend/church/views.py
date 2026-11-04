from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.views import APIView
from accounts.permissions import CanManageUsers
from .models import ChurchProfile
from .serializers import ChurchProfileSerializer
class ChurchProfileView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def get_permissions(self): return [] if self.request.method=='GET' else [CanManageUsers()]
    def get(self, request):
        obj,_=ChurchProfile.objects.get_or_create(pk=1); return Response(ChurchProfileSerializer(obj,context={'request':request}).data)
    def put(self, request):
        obj,_=ChurchProfile.objects.get_or_create(pk=1); s=ChurchProfileSerializer(obj,data=request.data,partial=True,context={'request':request}); s.is_valid(raise_exception=True); s.save(); return Response(s.data)
