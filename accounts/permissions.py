from rest_framework.permissions import BasePermission

# ---------------------------------------------------------------------------
# Role-based permission classes
# All RBAC is enforced server-side here, never in the frontend.
# ---------------------------------------------------------------------------


class IsAdmin(BasePermission):
    """Only users with role='admin' may access."""
    message = "Admin access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'employee')
            and request.user.employee.role == 'admin'
        )


class IsAssetManager(BasePermission):
    """Asset Managers (or higher) may access."""
    message = "Asset Manager access required."

    ALLOWED = ('admin', 'asset_manager')

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'employee')
            and request.user.employee.role in self.ALLOWED
        )


class IsAdminOrAssetManager(BasePermission):
    """Alias for IsAssetManager — kept for readability at call sites."""
    message = "Admin or Asset Manager access required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'employee')
            and request.user.employee.role in ('admin', 'asset_manager')
        )


class IsDepartmentHead(BasePermission):
    """Department Heads (or higher) may access."""
    message = "Department Head access required."

    ALLOWED = ('admin', 'asset_manager', 'department_head')

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'employee')
            and request.user.employee.role in self.ALLOWED
        )


class IsEmployee(BasePermission):
    """Any authenticated user with an Employee profile."""
    message = "Employee profile required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'employee')
        )


class IsAdminOrReadOnly(BasePermission):
    """Safe methods for any authenticated Employee; writes restricted to Admin."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and hasattr(request.user, 'employee')):
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.employee.role == 'admin'
