from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active')
        read_only_fields = ('id', 'email', 'role', 'is_active')


class StaffChoiceSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'full_name', 'role')

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.email


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_approved', 'last_login', 'date_joined', 'password')
        read_only_fields = ('id', 'is_approved', 'last_login', 'date_joined')

    def validate_email(self, value):
        queryset = User.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Ya existe un usuario con este correo.')
        return value

    def validate(self, attrs):
        if not self.instance:
            if not attrs.get('password'):
                raise serializers.ValidationError({'password': 'La contraseña inicial es obligatoria.'})
            return attrs
        requester = self.context['request'].user
        if self.instance.is_superuser and not requester.is_superuser:
            raise serializers.ValidationError('Solo un superusuario puede modificar a otro superusuario.')
        role = attrs.get('role', self.instance.role)
        is_active = attrs.get('is_active', self.instance.is_active)
        if self.instance == requester and (role != self.instance.role or not is_active):
            raise serializers.ValidationError('No puedes cambiar tu propio rol ni desactivar tu cuenta.')
        if is_active and not self.instance.is_approved:
            raise serializers.ValidationError({'is_active': 'Aprueba la solicitud antes de activar al usuario.'})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        if 'email' in validated_data:
            instance.username = validated_data['email']
        return super().update(instance, validated_data)


class ApprovalSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        # El registro público solo crea una solicitud: no da acceso hasta que un administrador la aprueba.
        return User.objects.create_user(**validated_data, is_active=False, is_approved=False)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        user = authenticate(email=attrs['email'], password=attrs['password'])
        if not user or not user.is_active:
            raise serializers.ValidationError('Correo o contraseña inválidos.')
        attrs['user'] = user
        return attrs

    @staticmethod
    def response_data(user):
        refresh = RefreshToken.for_user(user)
        return {'access': str(refresh.access_token), 'refresh': str(refresh), 'user': UserSerializer(user).data}


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate(self, attrs):
        try:
            user = User.objects.get(pk=force_str(urlsafe_base64_decode(attrs['uid'])), is_active=True)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            raise serializers.ValidationError('El enlace de recuperación no es válido.')
        if not default_token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError('El enlace de recuperación expiró o no es válido.')
        attrs['user'] = user
        return attrs
