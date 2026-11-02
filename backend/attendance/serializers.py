from rest_framework import serializers

from events.models import Event
from members.models import Member
from .models import AttendanceRecord, AttendanceSession


class AttendanceRecordSerializer(serializers.ModelSerializer):
    member_name = serializers.CharField(source='member.__str__', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ('id', 'member', 'member_name', 'status', 'updated_at')
        read_only_fields = ('id', 'member_name', 'updated_at')


class AttendanceSessionSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.title', read_only=True)
    records = AttendanceRecordSerializer(many=True, read_only=True)
    present_count = serializers.SerializerMethodField()
    absent_count = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceSession
        fields = ('id', 'event', 'event_name', 'date', 'created_at', 'present_count', 'absent_count', 'records')
        read_only_fields = ('id', 'created_at', 'present_count', 'absent_count', 'records')

    def validate_event(self, event):
        if event.status == Event.Status.CANCELLED:
            raise serializers.ValidationError('No se puede registrar asistencia para un evento cancelado.')
        return event

    def get_present_count(self, obj):
        return sum(record.status == AttendanceRecord.Status.PRESENT for record in obj.records.all())

    def get_absent_count(self, obj):
        return sum(record.status == AttendanceRecord.Status.ABSENT for record in obj.records.all())


class AttendanceBulkUpdateSerializer(serializers.Serializer):
    records = serializers.ListField(child=serializers.DictField(), allow_empty=False)

    def validate_records(self, value):
        valid_statuses = set(AttendanceRecord.Status.values)
        for record in value:
            if set(record) != {'member', 'status'} or record['status'] not in valid_statuses:
                raise serializers.ValidationError('Cada registro requiere member y status válido.')
        return value
