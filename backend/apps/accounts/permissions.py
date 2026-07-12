"""
accounts.permissions
---------------------
Role-based DRF permission classes. These are the ONLY place where roles are
checked — never trust client-supplied role data.
"""
from rest_framework.permissions import BasePermission

from apps.accounts.models import Role


class IsAdmin(BasePermission):
    """Only users with the Admin role."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == Role.ADMIN
        )


class IsAssetManager(BasePermission):
    """Asset Manager or Admin."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (Role.ADMIN, Role.ASSET_MANAGER)
        )


class IsDepartmentHead(BasePermission):
    """Department Head, Asset Manager, or Admin."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role
            in (Role.ADMIN, Role.ASSET_MANAGER, Role.DEPARTMENT_HEAD)
        )


class IsEmployee(BasePermission):
    """Any authenticated employee (all roles)."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsAdminOrReadOnly(BasePermission):
    """Admins can write; anyone authenticated can read."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return request.user.role == Role.ADMIN


class IsSelfOrAdmin(BasePermission):
    """User can access their own record; Admins can access any."""

    def has_object_permission(self, request, view, obj):
        return request.user.role == Role.ADMIN or obj == request.user
