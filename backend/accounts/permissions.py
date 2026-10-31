from rest_framework.permissions import BasePermission

from .models import User


class HasRole(BasePermission):
    allowed_roles = ()

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (
            request.user.is_superuser or request.user.role in self.allowed_roles
        ))


class CanManageUsers(HasRole):
    allowed_roles = (User.Role.ADMINISTRATOR,)


class CanManageFinances(HasRole):
    allowed_roles = (User.Role.ADMINISTRATOR, User.Role.TREASURER)
