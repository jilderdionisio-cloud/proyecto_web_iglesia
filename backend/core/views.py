from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Endpoint mínimo para comprobar la conexión entre React y Django."""
    return Response({'status': 'ok', 'message': 'API de Proyecto Web Iglesia activa'})
