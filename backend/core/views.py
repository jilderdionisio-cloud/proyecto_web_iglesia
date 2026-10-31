from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def health_check(request):
    """Endpoint mínimo para comprobar la conexión entre React y Django."""
    return Response({'status': 'ok', 'message': 'API de Proyecto Web Iglesia activa'})
