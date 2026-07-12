from rest_framework import serializers
from django.utils import timezone
from .models import MaintenanceRequest
from assets.models import Asset


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.asset_tag', read_only=True)
    raised_by_name = serializers.CharField(source='raised_by.full_name', read_only=True, default=None)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True, default=None)
    technician_name = serializers.CharField(source='technician.full_name', read_only=True, default=None)

    class Meta:
        model = MaintenanceRequest
        fields = (
            'id', 'asset', 'asset_tag',
            'raised_by', 'raised_by_name',
            'issue_description', 'priority', 'photo',
            'status', 'approved_by', 'approved_by_name',
            'technician', 'technician_name',
            'resolution_notes', 'resolved_at',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'raised_by', 'approved_by', 'resolved_at', 'created_at', 'updated_at')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee'):
            validated_data['raised_by'] = request.user.employee
        return super().create(validated_data)


class MaintenanceStatusUpdateSerializer(serializers.Serializer):
    """
    Used for PATCH /maintenance/<pk>/transition/
    Validates transition against the allowed state machine.
    Drives asset.status changes for approve and resolve transitions.
    """
    new_status = serializers.ChoiceField(choices=MaintenanceRequest.STATUS_CHOICES)
    technician = serializers.PrimaryKeyRelatedField(
        queryset=__import__('accounts').models.Employee.objects.all(),
        required=False,
        allow_null=True,
    )
    resolution_notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        instance = self.context['instance']
        new_status = data['new_status']
        allowed = MaintenanceRequest.ALLOWED_TRANSITIONS.get(instance.status, [])
        if new_status not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition from '{instance.status}' to '{new_status}'. "
                f"Allowed: {allowed}"
            )
        if new_status == 'assigned' and not data.get('technician'):
            raise serializers.ValidationError("A technician must be assigned when approving for work.")
        if new_status == 'resolved' and not data.get('resolution_notes'):
            raise serializers.ValidationError("resolution_notes is required when resolving.")
        return data

    def save(self, **kwargs):
        instance = self.context['instance']
        request = self.context.get('request')
        new_status = self.validated_data['new_status']

        instance.status = new_status

        if new_status == 'approved':
            instance.approved_by = request.user.employee if request else None
            # Asset status → Under Maintenance
            Asset.objects.filter(pk=instance.asset_id).update(status='under_maintenance')

        if new_status == 'assigned':
            instance.technician = self.validated_data.get('technician')

        if new_status == 'resolved':
            instance.resolution_notes = self.validated_data.get('resolution_notes', '')
            instance.resolved_at = timezone.now()
            # Asset status → Available
            Asset.objects.filter(pk=instance.asset_id).update(status='available')

        instance.save()
        return instance
