from rest_framework import serializers

from accounts.models import User
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    responsible_name = serializers.CharField(source='responsible.get_full_name', read_only=True)

    class Meta:
        model = Event
        fields = ('id', 'title', 'description', 'starts_at', 'ends_at', 'location', 'responsible', 'responsible_name', 'status', 'cancellation_reason', 'created_at', 'updated_at')
        read_only_fields = ('id', 'responsible', 'responsible_name', 'status', 'cancellation_reason', 'created_at', 'updated_at')

    def validate(self, attrs):
        ends_at = attrs.get('ends_at')
        starts_at = attrs.get('starts_at', getattr(self.instance, 'starts_at', None))
        if ends_at and starts_at and ends_at <= starts_at:
            raise serializers.ValidationError({'ends_at': 'La fecha de fin debe ser posterior al inicio.'})
        return attrs
