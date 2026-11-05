from rest_framework import serializers

from accounts.models import User
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    responsible = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_active=True), required=False)
    responsible_name = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'starts_at', 'ends_at', 'location', 'responsible', 'responsible_name', 'status', 'cancellation_reason', 'created_at', 'updated_at')
        read_only_fields = ('id', 'responsible_name', 'status', 'cancellation_reason', 'created_at', 'updated_at')

    def get_responsible_name(self, obj):
        return obj.responsible.get_full_name() or obj.responsible.email

    def validate(self, attrs):
        if self.instance and self.instance.status == Event.Status.CANCELLED:
            raise serializers.ValidationError('Un evento cancelado no se puede modificar.')
        ends_at = attrs.get('ends_at', getattr(self.instance, 'ends_at', None))
        starts_at = attrs.get('starts_at', getattr(self.instance, 'starts_at', None))
        if ends_at and starts_at and ends_at <= starts_at:
            raise serializers.ValidationError({'ends_at': 'La fecha de fin debe ser posterior al inicio.'})
        return attrs
