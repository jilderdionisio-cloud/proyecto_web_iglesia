from django.contrib import admin

from .models import Ministry, MinistryMembership


class MinistryMembershipInline(admin.TabularInline):
    model = MinistryMembership
    extra = 0


@admin.register(Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ('name', 'coordinator', 'is_active')
    inlines = (MinistryMembershipInline,)
