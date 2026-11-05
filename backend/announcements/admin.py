from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at', 'expires_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'body')
