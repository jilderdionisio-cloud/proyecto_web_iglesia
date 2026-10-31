from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'email', 'phone', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
