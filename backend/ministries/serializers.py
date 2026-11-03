from rest_framework import serializers

from accounts.models import User
from members.models import Member
from .models import Ministry, MinistryMembership
from .models import MinistryActivity


class MinistryMemberSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='member.__str__', read_only=True)
    member_id = serializers.IntegerField(source='member.id', read_only=True)

    class Meta:
        model = MinistryMembership
        fields = ('member_id', 'full_name', 'joined_at')


class MinistrySerializer(serializers.ModelSerializer):
    coordinator_name = serializers.CharField(source='coordinator.get_full_name', read_only=True)
    members = MinistryMemberSerializer(source='memberships', many=True, read_only=True)

    class Meta:
        model = Ministry
        fields = ('id', 'name', 'description', 'coordinator', 'coordinator_name', 'is_active', 'created_at', 'members')
        read_only_fields = ('id', 'coordinator_name', 'created_at', 'members')

    def validate_coordinator(self, coordinator):
        if not coordinator.is_active:
            raise serializers.ValidationError('El coordinador debe ser un usuario activo.')
        return coordinator


class MemberAssignmentSerializer(serializers.Serializer):
    member = serializers.PrimaryKeyRelatedField(queryset=Member.objects.filter(is_active=True))

class MinistryActivitySerializer(serializers.ModelSerializer):
    class Meta: model=MinistryActivity; fields=('id','ministry','title','scheduled_at','description'); read_only_fields=('id',)
