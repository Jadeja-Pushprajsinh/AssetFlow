from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Employee


# ---------------------------------------------------------------------------
# Signup — role is ALWAYS set to 'employee'; any role field in the request body
# is silently ignored.  This is enforced here, not in the view.
# ---------------------------------------------------------------------------
class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password'],
        )
        # Always create employee with role='employee' — never from request data
        Employee.objects.create(user=user, role='employee')
        return user


# ---------------------------------------------------------------------------
# Employee profile (read + limited self-update)
# ---------------------------------------------------------------------------
class EmployeeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True, default=None)

    class Meta:
        model = Employee
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'department', 'department_name', 'role', 'phone', 'profile_photo',
            'status', 'created_at',
        )
        read_only_fields = ('id', 'role', 'created_at')


# ---------------------------------------------------------------------------
# Role promotion — Admin-only endpoint
# Only 'role' and 'department' may be updated via this serializer.
# Status change also permitted by admin.
# ---------------------------------------------------------------------------
class RolePromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('role', 'department', 'status')

    def validate_role(self, value):
        allowed = [r[0] for r in Employee.ROLE_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(f"Role must be one of: {allowed}")
        return value


# ---------------------------------------------------------------------------
# Forgot-password — basic email-based stub (sends reset link in Phase 3)
# ---------------------------------------------------------------------------
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email__iexact=value).exists():
            # Don't reveal whether email exists — security best practice
            pass
        return value.lower()
