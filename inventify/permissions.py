from django.contrib.auth.models import AnonymousUser
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
        if isinstance(request.user, AnonymousUser):
            return False
        if request.user.is_superuser:
            return True
        user_roles = request.user.roles.values_list('name', flat=True)
        return any(role in self.allowed_roles for role in user_roles)


class InventifyAPIPermission(BasePermission):
    """
    Дает доступ только сотрудникам (через IsStaff) для URL, начинающихся с /api/admin.
    Остальные URL доступны для всех.
    """
    def has_permission(self, request, view):
        # Проверяем, начинается ли URL с /api/admin
        if request.path.startswith('/api/admin'):
            user = request.user
            if isinstance(user, AnonymousUser) or not user.is_authenticated:
                return False
            # Доступ в админку — только сотрудникам (is_staff) и суперпользователям
            return bool(user.is_superuser or user.is_staff)
        # Для всех остальных URL доступ разрешен
        return True
