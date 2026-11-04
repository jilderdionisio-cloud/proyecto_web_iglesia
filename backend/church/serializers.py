from rest_framework import serializers
from .models import ChurchProfile
class ChurchProfileSerializer(serializers.ModelSerializer):
    class Meta: model=ChurchProfile; fields=('id','name','logo','address','phone','email','regular_schedule','updated_at'); read_only_fields=('id','updated_at')
    def validate_logo(self, logo):
        if logo.size > 2 * 1024 * 1024:
            raise serializers.ValidationError('El logotipo no debe superar 2 MB.')
        if getattr(logo, 'content_type', '') not in ('image/jpeg', 'image/png', 'image/webp'):
            raise serializers.ValidationError('Formato permitido: JPEG, PNG o WebP.')
        return logo
