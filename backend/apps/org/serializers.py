"""
org.serializers
"""
from rest_framework import serializers
from apps.org.models import Department, AssetCategory


class DepartmentSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="parent_department.name", read_only=True, allow_null=True
    )
    head_name = serializers.SerializerMethodField()
    employee_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = [
            "id", "name", "code", "parent_department", "parent_name",
            "head", "head_name", "is_active", "employee_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_head_name(self, obj):
        if obj.head:
            return obj.head.get_full_name()
        return None

    def get_employee_count(self, obj):
        return obj.employees.filter(status="active").count()

    def validate_code(self, value):
        return value.upper()


class AssetCategorySerializer(serializers.ModelSerializer):
    asset_count = serializers.SerializerMethodField()

    class Meta:
        model = AssetCategory
        fields = [
            "id", "name", "description", "custom_fields", "is_active",
            "asset_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_asset_count(self, obj):
        return obj.assets.count()

    def validate_custom_fields(self, value):
        """
        Validate custom_fields schema:
        Must be a list of objects with at least a 'name' and 'type' key.
        Allowed types: text, integer, decimal, date, boolean.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("custom_fields must be a list.")
        allowed_types = {"text", "integer", "decimal", "date", "boolean"}
        for field in value:
            if not isinstance(field, dict):
                raise serializers.ValidationError("Each custom field must be an object.")
            if "name" not in field or "type" not in field:
                raise serializers.ValidationError(
                    "Each custom field must have 'name' and 'type'."
                )
            if field["type"] not in allowed_types:
                raise serializers.ValidationError(
                    f"Type '{field['type']}' is not allowed. "
                    f"Allowed: {', '.join(allowed_types)}"
                )
        return value
