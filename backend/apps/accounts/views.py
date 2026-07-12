"""
accounts.views
--------------
All views delegate validation to serializers and business logic to services.
Views only handle HTTP concerns (status codes, response shape).
"""
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.models import Employee
from apps.accounts.permissions import IsAdmin, IsSelfOrAdmin
from apps.accounts.serializers import (
    SignupSerializer,
    LoginSerializer,
    TokenPairSerializer,
    EmployeeListSerializer,
    EmployeeDetailSerializer,
    RolePromotionSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


# ── Auth endpoints ────────────────────────────────────────────────────────────

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = TokenPairSerializer.for_user(user)
        return Response(
            TokenPairSerializer(tokens).data, status=status.HTTP_201_CREATED
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = TokenPairSerializer.for_user(user)
        return Response(TokenPairSerializer(tokens).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            pass  # Already invalid — still return 204
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = Employee.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            send_mail(
                subject="AssetFlow — Password Reset",
                message=f"Click the link to reset your password: {reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Employee.DoesNotExist:
            pass  # Don't reveal whether email exists
        # Always return 200 to prevent email enumeration
        return Response(
            {"detail": "If that email is registered, a reset link has been sent."}
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
            user = Employee.objects.get(pk=uid)
        except (Employee.DoesNotExist, ValueError, TypeError):
            return Response(
                {"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not default_token_generator.check_token(user, serializer.validated_data["token"]):
            return Response(
                {"detail": "Reset link expired or invalid."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password reset successful."})


# ── Profile ───────────────────────────────────────────────────────────────────

class MeView(generics.RetrieveUpdateAPIView):
    """Logged-in user's own profile."""
    serializer_class = EmployeeDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Employee Directory ────────────────────────────────────────────────────────

class EmployeeListView(generics.ListAPIView):
    """
    GET /api/v1/auth/employees/
    All authenticated users can list employees (for allocation dropdowns etc).
    Admins can filter by role; others see active employees only.
    """
    serializer_class = EmployeeListSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ["first_name", "last_name", "email", "employee_id"]
    ordering_fields = ["first_name", "last_name", "role", "created_at"]
    ordering = ["first_name"]

    def get_queryset(self):
        qs = Employee.objects.select_related("department").filter(status="active")
        role = self.request.query_params.get("role")
        department = self.request.query_params.get("department")
        if role:
            qs = qs.filter(role=role)
        if department:
            qs = qs.filter(department_id=department)
        return qs


class EmployeeDetailView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/v1/auth/employees/{id}/
    Admins can update any employee. Employees can only view (IsSelfOrAdmin for writes).
    """
    serializer_class = EmployeeDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Employee.objects.select_related("department").all()

    def update(self, request, *args, **kwargs):
        # Only Admins or the user themselves can update
        obj = self.get_object()
        if not (request.user.is_admin or request.user == obj):
            return Response(
                {"detail": "You do not have permission to edit this employee."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)


class RolePromotionView(APIView):
    """
    PATCH /api/v1/auth/employees/{id}/promote/
    Admin-only: promote or demote an employee's role.
    This endpoint enforces at the server level that only Admins can assign roles.
    """
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(
                {"detail": "Employee not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = RolePromotionSerializer(
            employee, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.update(employee, serializer.validated_data)

        # Log the activity
        from apps.notifications.services import log_activity
        log_activity(
            user=request.user,
            action="employee.role_changed",
            entity_type="Employee",
            entity_id=employee.id,
            details={"new_role": employee.role, "changed_by": request.user.email},
            request=request,
        )

        return Response(EmployeeDetailSerializer(employee).data)
