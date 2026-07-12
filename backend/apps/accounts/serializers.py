"""
accounts.serializers
---------------------
All request/response shapes for auth and employee management.
Business logic lives here or in services.py — not in views.
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import Employee, Role


# ── Auth serializers ──────────────────────────────────────────────────────────

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Employee
        fields = [
            "email", "username", "first_name", "last_name", "phone",
            "password", "password2",
        ]
        extra_kwargs = {
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        # Signup ALWAYS creates an Employee role — never trust client input
        user = Employee.objects.create_user(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data.get("phone"),
            password=validated_data["password"],
            role=Role.EMPLOYEE,  # hard-coded — clients cannot set role at signup
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            email=attrs["email"],
            password=attrs["password"],
        )
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if user.status != "active":
            raise serializers.ValidationError("Your account is inactive. Contact an Admin.")
        attrs["user"] = user
        return attrs


class TokenPairSerializer(serializers.Serializer):
    """Returns access + refresh token pair along with user profile."""
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return EmployeeProfileSerializer(obj["user"]).data

    @classmethod
    def for_user(cls, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": user,
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Employee.objects.filter(email=value).exists():
            # Don't reveal whether the email exists
            return value
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    uid = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password2 = serializers.CharField()

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password2"]:
            raise serializers.ValidationError({"new_password": "Passwords do not match."})
        return attrs


# ── Employee / profile serializers ────────────────────────────────────────────

class EmployeeProfileSerializer(serializers.ModelSerializer):
    """Lightweight read serializer — used in token response and list views."""
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            "id", "employee_id", "email", "first_name", "last_name",
            "phone", "avatar", "role", "status",
            "department", "department_name", "created_at",
        ]
        read_only_fields = [
            "id", "employee_id", "email", "role", "created_at",
        ]


class EmployeeListSerializer(serializers.ModelSerializer):
    """Used in the Employee Directory listing."""
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            "id", "employee_id", "first_name", "last_name", "email",
            "role", "status", "department", "department_name", "avatar",
        ]


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Full read/write serializer for an individual employee (self or Admin)."""
    department_name = serializers.CharField(
        source="department.name", read_only=True, allow_null=True
    )

    class Meta:
        model = Employee
        fields = [
            "id", "employee_id", "email", "username", "first_name", "last_name",
            "phone", "avatar", "role", "status", "department", "department_name",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "employee_id", "email", "created_at", "updated_at"]

    def validate_role(self, value):
        # Only Admins can set role; this validation is enforced in the view via
        # IsAdmin permission, but we double-check here
        request = self.context.get("request")
        if request and not request.user.is_admin and value != request.user.role:
            raise serializers.ValidationError("Only Admins can change roles.")
        return value


class RolePromotionSerializer(serializers.Serializer):
    """
    Admin-only: promote/demote an employee's role.
    Used by PATCH /api/v1/auth/employees/{id}/promote/
    """
    role = serializers.ChoiceField(choices=Role.choices)

    def update(self, instance, validated_data):
        instance.role = validated_data["role"]
        instance.save(update_fields=["role", "updated_at"])
        return instance
