from rest_framework import serializers

from members.models import Member
from .models import Ministry, MinistryActivity, MinistryMembership


class MinistryMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='member.__str__', read_only=True)
    member_id = serializers.IntegerField(source='member.id', read_only=True)

    class Meta:
        model = MinistryMembership
        fields = ('member_id', 'full_name', 'joined_at')


class MinistrySerializer(serializers.ModelSerializer):
    coordinator_name = serializers.SerializerMethodField()
    members = MinistryMemberSerializer(source='memberships', many=True, read_only=True)

    class Meta:
        model = Ministry
        fields = ('id', 'name', 'description', 'coordinator', 'coordinator_name', 'is_active', 'created_at', 'members')
        read_only_fields = ('id', 'coordinator_name', 'created_at', 'members')

    def get_coordinator_name(self, obj):
        return obj.coordinator.get_full_name() or obj.coordinator.email

    def validate_coordinator(self, coordinator):
        if not coordinator.is_active:
            raise serializers.ValidationError('El coordinador debe ser un usuario activo.')
        return coordinator


class MinistryActivitySerializer(serializers.ModelSerializer):
    ministry_name = serializers.CharField(source='ministry.name', read_only=True)

    class Meta:
        model = MinistryActivity
        fields = ('id', 'ministry', 'ministry_name', 'title', 'description', 'date', 'location', 'created_at')
        read_only_fields = ('id', 'ministry_name', 'created_at')

    def validate_ministry(self, ministry):
        if self.instance and ministry != self.instance.ministry:
            raise serializers.ValidationError('Una actividad no se puede mover a otro ministerio.')
        return ministry


class MemberAssignmentSerializer(serializers.Serializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.filter(is_active=True))
