from rest_framework import serializers

from .models import ChurchProfile, ServiceSchedule

MAX_LOGO_SIZE = 2 * 1024 * 1024
LOGO_FORMATS = ('PNG', 'JPEG', 'WEBP')


class ServiceScheduleSerializer(serializers.ModelSerializer):
    day_label = serializers.CharField(source='get_day_display', read_only=True)

    class Meta:
        model = ServiceSchedule
        fields = ('id', 'day', 'day_label', 'name', 'starts_at', 'ends_at')
        read_only_fields = ('id', 'day_label')

    def validate(self, attrs):
        starts_at = attrs.get('starts_at', getattr(self.instance, 'starts_at', None))
        ends_at = attrs.get('ends_at', getattr(self.instance, 'ends_at', None))
        if ends_at and starts_at and ends_at <= starts_at:
            raise serializers.ValidationError({'ends_at': 'La hora de fin debe ser posterior al inicio.'})
        return attrs


class ChurchProfileSerializer(serializers.ModelSerializer):
    remove_logo = serializers.BooleanField(write_only=True, required=False)
    schedules = serializers.SerializerMethodField()

    class Meta:
        model = ChurchProfile
        fields = ('name', 'description', 'logo', 'phone', 'email', 'website', 'address', 'city', 'state', 'postal_code', 'updated_at', 'remove_logo', 'schedules')
        read_only_fields = ('updated_at', 'schedules')

    def get_schedules(self, obj):
        return ServiceScheduleSerializer(ServiceSchedule.objects.all(), many=True).data

    def validate_logo(self, logo):
        if logo.size > MAX_LOGO_SIZE:
            raise serializers.ValidationError('El logo no debe superar los 2 MB.')
        if logo.image.format not in LOGO_FORMATS:
            raise serializers.ValidationError('El logo debe ser PNG, JPG o WEBP.')
        return logo

    def update(self, instance, validated_data):
        remove_logo = validated_data.pop('remove_logo', False)
        if instance.logo and (remove_logo or 'logo' in validated_data):
            instance.logo.delete(save=False)
        return super().update(instance, validated_data)
