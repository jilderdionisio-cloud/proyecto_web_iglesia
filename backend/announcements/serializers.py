from rest_framework import serializers
from .models import Announcement
class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ('id','title','body','published_at','is_published')
        read_only_fields = ('id','published_at')
