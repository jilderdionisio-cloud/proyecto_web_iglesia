from rest_framework.permissions import SAFE_METHODS, BasePermission

from .models import User

ADMINISTRATOR = User.Role.ADMINISTRATOR
PASTOR = User.Role.PASTOR
SECRETARY = User.Role.SECRETARY
TREASURER = User.Role.TREASURER
COORDINATOR = User.Role.COORDINATOR

ALL_ROLES = (ADMINISTRATOR, PASTOR, SECRETARY, TREASURER, COORDINATOR)
OPERATIONAL_ROLES = (ADMINISTRATOR, PASTOR, SECRETARY, COORDINATOR)
LEADERSHIP_ROLES = (ADMINISTRATOR, PASTOR, SECRETARY)


def is_scoped_coordinator(user):
    """Los coordinadores solo modifican lo que tienen asignado."""
    return user.role == COORDINATOR and not user.is_superuser


class HasRole(BasePermission):
    """Matriz de acceso: `allowed_roles` escribe y `read_roles` consulta (por defecto, los mismos)."""
    allowed_roles = ()
    read_roles = None

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True
        reading = request.method in SAFE_METHODS and self.read_roles is not None
        return request.user.role in (self.read_roles if reading else self.allowed_roles)


class CanManageUsers(HasRole):
    allowed_roles = (ADMINISTRATOR,)


class CanListStaff(HasRole):
    allowed_roles = OPERATIONAL_ROLES


class CanManageFinances(HasRole):
    allowed_roles = (ADMINISTRATOR, TREASURER)


class CanViewFinancialSummary(HasRole):
    allowed_roles = (ADMINISTRATOR, TREASURER, PASTOR)


class CanManageMembers(HasRole):
    allowed_roles = LEADERSHIP_ROLES
    read_roles = ALL_ROLES


class CanManageEvents(HasRole):
    allowed_roles = OPERATIONAL_ROLES
    read_roles = ALL_ROLES

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or not is_scoped_coordinator(request.user):
            return True
        return obj.responsible_id == request.user.id


class CanManageAttendance(HasRole):
    allowed_roles = OPERATIONAL_ROLES


class CanManageMinistries(HasRole):
    allowed_roles = OPERATIONAL_ROLES
    read_roles = ALL_ROLES

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return not (is_scoped_coordinator(request.user) and view.action in ('create', 'destroy'))

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or not is_scoped_coordinator(request.user):
            return True
        return obj.coordinator_id == request.user.id


class CanManageMinistryActivities(HasRole):
    allowed_roles = OPERATIONAL_ROLES
    read_roles = ALL_ROLES

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS or not is_scoped_coordinator(request.user):
            return True
        return obj.ministry.coordinator_id == request.user.id


class CanManageAnnouncements(HasRole):
    allowed_roles = LEADERSHIP_ROLES
    read_roles = ALL_ROLES


class CanManageChurch(HasRole):
    allowed_roles = (ADMINISTRATOR,)


class CanViewOperationalReports(HasRole):
    allowed_roles = LEADERSHIP_ROLES
