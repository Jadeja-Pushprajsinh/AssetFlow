from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import Employee
from .serializers import (
    SignupSerializer,
    EmployeeSerializer,
    RolePromotionSerializer,
    ForgotPasswordSerializer,
)
from .permissions import IsAdmin, IsEmployee


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------
class SignupView(generics.CreateAPIView):
    """
    POST /api/auth/signup/
    Creates a User + Employee(role='employee').  No role field accepted.
    """
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {'detail': 'Account created. Please log in.'},
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# JWT login / refresh
# ---------------------------------------------------------------------------
class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — returns access + refresh tokens."""
    permission_classes = [AllowAny]


class TokenRefreshAPIView(TokenRefreshView):
    """POST /api/auth/token/refresh/"""
    permission_classes = [AllowAny]


# ---------------------------------------------------------------------------
# Current user profile
# ---------------------------------------------------------------------------
class MeView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/auth/me/  — own profile
    PATCH /api/auth/me/ — update phone / profile_photo only
    """
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee]

    def get_object(self):
        return self.request.user.employee


# ---------------------------------------------------------------------------
# Employee directory
# ---------------------------------------------------------------------------
class EmployeeListView(generics.ListAPIView):
    """GET /api/auth/employees/ — paginated employee list."""
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee]
    queryset = Employee.objects.select_related('user', 'department').all()
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'user__username']
    filterset_fields = ['role', 'status', 'department']
    ordering_fields = ['user__first_name', 'created_at', 'role']
    ordering = ['user__first_name']


class EmployeeDetailView(generics.RetrieveAPIView):
    """GET /api/auth/employees/<pk>/"""
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee]
    queryset = Employee.objects.select_related('user', 'department').all()


# ---------------------------------------------------------------------------
# Role promotion — Admin ONLY
# ---------------------------------------------------------------------------
class RolePromotionView(generics.UpdateAPIView):
    """
    PATCH /api/auth/employees/<pk>/promote/
    Admin-only: change role, department, or status of any employee.
    """
    serializer_class = RolePromotionSerializer
    permission_classes = [IsAdmin]
    queryset = Employee.objects.select_related('user').all()
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Forgot password — stub
# ---------------------------------------------------------------------------
class ForgotPasswordView(APIView):
    """POST /api/auth/forgot-password/"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO Phase 3: send reset email
        return Response(
            {'detail': 'If that email is registered, a reset link has been sent.'},
            status=status.HTTP_200_OK,
        )
