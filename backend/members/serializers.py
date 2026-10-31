from rest_framework import serializers

from .models import Member


class MemberSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = ('id', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'address', 'birth_date', 'joined_at', 'is_active', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'full_name', 'joined_at', 'created_at', 'updated_at')

    def get_full_name(self, obj):
        return str(obj)
