"""
assets.serializers
"""
from rest_framework import serializers
from apps.assets.models import Asset, AssetStatus, ASSET_STATUS_TRANSITIONS
from apps.org.models import AssetCategory


class AssetListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list/search views."""
    category_name = serializers.CharField(source="category.name", read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            "id", "asset_tag", "name", "category", "category_name",
            "status", "condition", "location", "is_bookable",
            "created_by_name", "created_at",
        ]

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class AssetDetailSerializer(serializers.ModelSerializer):
    """Full serializer for create/retrieve/update."""
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Asset
        fields = [
            "id", "asset_tag", "name", "category", "category_name",
            "serial_number", "acquisition_date", "acquisition_cost",
            "condition", "location", "is_bookable", "status",
            "custom_field_values", "photo", "documents",
            "created_by", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "asset_tag", "created_by", "created_at", "updated_at"]

    def validate_custom_field_values(self, value):
        """
        Validate that custom_field_values conforms to the category's custom_fields schema.
        """
        category_id = self.initial_data.get("category") or (
            self.instance.category_id if self.instance else None
        )
        if not category_id:
            return value
        try:
            category = AssetCategory.objects.get(pk=category_id)
        except AssetCategory.DoesNotExist:
            return value

        schema = category.custom_fields or []
        errors = {}
        for field_def in schema:
            field_name = field_def.get("name")
            required = field_def.get("required", False)
            if required and field_name not in value:
                errors[field_name] = f"This field is required for category '{category.name}'."
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def validate_status(self, value):
        """
        Enforce the asset status state machine.
        Direct status changes via the API are only allowed for Retired/Disposed transitions.
        Other transitions go through domain-specific endpoints (allocation, maintenance, audit).
        """
        if self.instance:
            current = self.instance.status
            allowed = ASSET_STATUS_TRANSITIONS.get(current, [])
            if value != current and value not in allowed:
                raise serializers.ValidationError(
                    f"Cannot transition asset from '{current}' to '{value}'."
                )
        return value

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
