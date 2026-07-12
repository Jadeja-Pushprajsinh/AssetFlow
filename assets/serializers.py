from rest_framework import serializers
from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)

    class Meta:
        model = Asset
        fields = (
            'id', 'name', 'category', 'category_name',
            'asset_tag', 'serial_number',
            'acquisition_date', 'acquisition_cost',
            'condition', 'condition_display',
            'location', 'is_bookable',
            'status', 'status_display',
            'custom_field_values',
            'photo', 'documents',
            'created_by', 'created_by_name',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'asset_tag', 'created_at', 'updated_at')

    def validate_status(self, value):
        """
        Direct status changes are ONLY allowed for non-workflow transitions.
        Maintenance-driven (under_maintenance/available) and audit-driven (lost)
        transitions are blocked here — they must go through their respective workflows.
        """
        WORKFLOW_ONLY_STATUSES = ('under_maintenance', 'lost')
        if value in WORKFLOW_ONLY_STATUSES:
            raise serializers.ValidationError(
                f"Status '{value}' can only be set via the maintenance or audit workflow."
            )
        return value

    def create(self, validated_data):
        # Attach the creating employee automatically
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee'):
            validated_data['created_by'] = request.user.employee
        return super().create(validated_data)


class AssetListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list endpoints — omits large fields."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Asset
        fields = (
            'id', 'name', 'asset_tag', 'category', 'category_name',
            'status', 'status_display', 'location', 'condition', 'is_bookable',
        )
