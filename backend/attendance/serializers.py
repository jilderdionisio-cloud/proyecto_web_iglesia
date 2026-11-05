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


class AttendanceHistorySerializer(AttendanceRecordSerializer):
    event = serializers.IntegerField(source='session.event_id', read_only=True)
    event_name = serializers.CharField(source='session.event.title', read_only=True)
    date = serializers.DateField(source='session.date', read_only=True)
    marked_by_name = serializers.SerializerMethodField()

    class Meta(AttendanceRecordSerializer.Meta):
        fields = AttendanceRecordSerializer.Meta.fields + ('event', 'event_name', 'date', 'marked_by_name')

    def get_marked_by_name(self, obj):
        return obj.marked_by.get_full_name() or obj.marked_by.email


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
            if set(record) != {'member', 'status'} or record['status'] not in valid_statuses or not isinstance(record['member'], int):
                raise serializers.ValidationError('Cada registro requiere member y status válido.')
        return value
