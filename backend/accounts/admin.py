from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_approved')
    list_filter = ('role', 'is_active', 'is_approved', 'is_staff')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (('Rol de iglesia', {'fields': ('role', 'is_approved')}),)
    add_fieldsets = UserAdmin.add_fieldsets + (('Rol de iglesia', {'fields': ('email', 'role')}),)
