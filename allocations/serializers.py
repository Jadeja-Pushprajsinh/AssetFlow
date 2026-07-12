from rest_framework import serializers
from django.db import transaction
from django.utils import timezone

from .models import Allocation, TransferRequest
from assets.models import Asset


class AllocationSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.asset_tag', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    holder_employee_name = serializers.CharField(
        source='holder_employee.full_name', read_only=True, default=None
    )
    holder_department_name = serializers.CharField(
        source='holder_department.name', read_only=True, default=None
    )
    allocated_by_name = serializers.CharField(
        source='allocated_by.full_name', read_only=True, default=None
    )

    class Meta:
        model = Allocation
        fields = (
            'id', 'asset', 'asset_tag', 'asset_name',
            'holder_type', 'holder_employee', 'holder_employee_name',
            'holder_department', 'holder_department_name',
            'allocated_date', 'expected_return_date', 'actual_return_date',
            'status', 'return_notes', 'allocated_by', 'allocated_by_name',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'status', 'allocated_by', 'created_at', 'updated_at')

    def validate(self, data):
        holder_type = data.get('holder_type')
        if holder_type == 'employee' and not data.get('holder_employee'):
            raise serializers.ValidationError("holder_employee is required when holder_type is 'employee'.")
        if holder_type == 'department' and not data.get('holder_department'):
            raise serializers.ValidationError("holder_department is required when holder_type is 'department'.")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        asset = validated_data['asset']

        with transaction.atomic():
            # Lock the asset row to prevent concurrent double-allocation
            locked_asset = Asset.objects.select_for_update().get(pk=asset.pk)

            if locked_asset.status == 'allocated':
                raise serializers.ValidationError(
                    "This asset is already allocated. Initiate a transfer request instead."
                )
            if locked_asset.status != 'available':
                raise serializers.ValidationError(
                    f"Asset cannot be allocated in its current status: '{locked_asset.get_status_display()}'."
                )

            if request and hasattr(request.user, 'employee'):
                validated_data['allocated_by'] = request.user.employee

            if not validated_data.get('allocated_date'):
                validated_data['allocated_date'] = timezone.now().date()

            allocation = Allocation.objects.create(**validated_data)
            # Update asset status atomically
            Asset.objects.filter(pk=asset.pk).update(status='allocated')
            return allocation


class ReturnSerializer(serializers.ModelSerializer):
    """Used for the return workflow — marks an active allocation as returned."""
    class Meta:
        model = Allocation
        fields = ('actual_return_date', 'return_notes')

    def update(self, instance, validated_data):
        if instance.status != 'active':
            raise serializers.ValidationError("Only active allocations can be returned.")

        validated_data['status'] = 'returned'
        if not validated_data.get('actual_return_date'):
            validated_data['actual_return_date'] = timezone.now().date()

        with transaction.atomic():
            allocation = super().update(instance, validated_data)
            Asset.objects.filter(pk=instance.asset_id).update(status='available')
            return allocation


class TransferRequestSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.asset_tag', read_only=True)
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True, default=None)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True, default=None)

    class Meta:
        model = TransferRequest
        fields = (
            'id', 'asset', 'asset_tag',
            'from_employee', 'from_department',
            'to_employee', 'to_department',
            'status', 'requested_by', 'requested_by_name',
            'approved_by', 'approved_by_name',
            'notes', 'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'status', 'requested_by', 'approved_by', 'created_at', 'updated_at')

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee'):
            validated_data['requested_by'] = request.user.employee
        return super().create(validated_data)
