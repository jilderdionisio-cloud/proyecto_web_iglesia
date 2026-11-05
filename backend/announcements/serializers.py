from django.utils import timezone
from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = ('id', 'title', 'body', 'is_published', 'published_at', 'expires_at', 'author', 'author_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'is_published', 'published_at', 'author', 'author_name', 'created_at', 'updated_at')

    def get_author_name(self, obj):
        return obj.author.get_full_name() or obj.author.email

    def validate_expires_at(self, value):
        if value and value <= timezone.now():
            raise serializers.ValidationError('La vigencia debe terminar en el futuro.')
        return value
