from rest_framework.permissions import BasePermission

from users.enums import RoleEnum


class IsManager(BasePermission):
    """
    Разрешение для Менеджера компании
    """

    allowed_roles = [RoleEnum.DEPARTMENT_DIRECTOR.value, RoleEnum.DIRECTOR.value]

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        user_roles = request.user.roles.values_list('name', flat=True)
        return any(role in self.allowed_roles for role in user_roles)


class IsDirector(BasePermission):
    """
    Разрешение только для Директора.
    """

    allowed_roles = [RoleEnum.DIRECTOR.value]

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        user_roles = request.user.roles.values_list('name', flat=True)
        return any(role in self.allowed_roles for role in user_roles)


class IsStaff(BasePermission):
    """
        Разрешение только для сотрудников.
    """

    allowed_roles = [role.value for role in (RoleEnum)]

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        user_roles = request.user.roles.values_list('name', flat=True)
        return any(role in self.allowed_roles for role in user_roles)
