import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from core.pagination import OptionalPageNumberPagination
from .models import User
from .permissions import CanListStaff, CanManageUsers
from .serializers import (
    ApprovalSerializer, LoginSerializer, PasswordResetConfirmSerializer, RegisterSerializer,
    StaffChoiceSerializer, UserAdminSerializer, UserSerializer,
)

logger = logging.getLogger(__name__)


def revoke_user_tokens(user):
    for token in OutstandingToken.objects.filter(user=user):
        BlacklistedToken.objects.get_or_create(token=token)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.response_data(serializer.validated_data['user']))


class LogoutView(APIView):
    def post(self, request):
        try:
            RefreshToken(request.data['refresh']).blacklist()
        except (KeyError, TokenError):
            return Response({'detail': 'Token de actualización inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email', '').strip()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f'{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}'
            try:
                send_mail('Recuperación de contraseña', f'Usa este enlace para cambiar tu contraseña: {reset_url}', settings.DEFAULT_FROM_EMAIL, [user.email])
            except OSError:
                # Responder igual evita revelar si el correo existe; el fallo queda en el log.
                logger.exception('No se pudo enviar el correo de recuperación.')
        return Response({'detail': 'Si el correo existe, se enviaron instrucciones de recuperación.'})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user.set_password(serializer.validated_data['password'])
        user.save(update_fields=['password'])
        revoke_user_tokens(user)
        return Response({'detail': 'Contraseña actualizada correctamente.'})


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserAdminSerializer
    permission_classes = (CanManageUsers,)
    http_method_names = ('get', 'post', 'patch', 'head', 'options')
    pagination_class = OptionalPageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ('email', 'first_name', 'last_name')

    def get_queryset(self):
        queryset = User.objects.order_by('email')
        role = self.request.query_params.get('role')
        if role in User.Role.values:
            queryset = queryset.filter(role=role)
        state = self.request.query_params.get('state')
        if state == 'pending':
            queryset = queryset.filter(is_approved=False)
        elif state == 'active':
            queryset = queryset.filter(is_active=True)
        elif state == 'inactive':
            queryset = queryset.filter(is_active=False, is_approved=True)
        return queryset

    def get_permissions(self):
        if self.action == 'choices':
            return [CanListStaff()]
        return super().get_permissions()

    def perform_update(self, serializer):
        user = serializer.save()
        if not user.is_active or 'password' in serializer.validated_data:
            revoke_user_tokens(user)

    @action(detail=False, methods=('get',), pagination_class=None)
    def choices(self, request):
        users = User.objects.filter(is_active=True).order_by('first_name', 'last_name', 'email')
        return Response(StaffChoiceSerializer(users, many=True).data)

    @action(detail=True, methods=('post',))
    def approve(self, request, pk=None):
        user = self.get_object()
        if user.is_approved:
            return Response({'detail': 'Este usuario ya fue aprobado.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.role = serializer.validated_data.get('role', user.role)
        user.is_approved = True
        user.is_active = True
        user.save(update_fields=('role', 'is_approved', 'is_active'))
        return Response(self.get_serializer(user).data)

    @action(detail=True, methods=('post',))
    def reject(self, request, pk=None):
        user = self.get_object()
        if user.is_approved:
            return Response({'detail': 'Solo se pueden rechazar solicitudes pendientes.'}, status=status.HTTP_400_BAD_REQUEST)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
