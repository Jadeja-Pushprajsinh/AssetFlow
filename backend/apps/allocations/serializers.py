"""
allocations.serializers
-----------------------
Allocation creation enforces double-allocation prevention via
transaction.atomic() + select_for_update() in services.py.
"""
from rest_framework import serializers
from django.utils import timezone

from apps.allocations.models import Allocation, TransferRequest, AllocationStatus


class AllocationListSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)
    asset_name = serializers.CharField(source="asset.name", read_only=True)
    holder_name = serializers.SerializerMethodField()

    class Meta:
        model = Allocation
        fields = [
            "id", "asset", "asset_tag", "asset_name",
            "holder_type", "holder_employee", "holder_department", "holder_name",
            "allocated_date", "expected_return_date", "actual_return_date",
            "status", "created_at",
        ]

    def get_holder_name(self, obj):
        if obj.holder_type == "employee" and obj.holder_employee:
            return obj.holder_employee.get_full_name()
        if obj.holder_type == "department" and obj.holder_department:
            return obj.holder_department.name
        return None


class AllocationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = [
            "asset", "holder_type", "holder_employee", "holder_department",
            "allocated_date", "expected_return_date",
        ]

    def validate(self, attrs):
        holder_type = attrs.get("holder_type")
        if holder_type == "employee" and not attrs.get("holder_employee"):
            raise serializers.ValidationError({"holder_employee": "Required when holder_type is 'employee'."})
        if holder_type == "department" and not attrs.get("holder_department"):
            raise serializers.ValidationError({"holder_department": "Required when holder_type is 'department'."})
        return attrs

    def create(self, validated_data):
        from apps.allocations.services import create_allocation
        return create_allocation(
            asset=validated_data["asset"],
            holder_type=validated_data["holder_type"],
            holder_employee=validated_data.get("holder_employee"),
            holder_department=validated_data.get("holder_department"),
            allocated_by=self.context["request"].user,
            allocated_date=validated_data.get("allocated_date", timezone.now().date()),
            expected_return_date=validated_data.get("expected_return_date"),
        )


class AllocationReturnSerializer(serializers.Serializer):
    return_notes = serializers.CharField(required=False, allow_blank=True)
    condition = serializers.ChoiceField(
        choices=["New", "Good", "Fair", "Poor"], required=False
    )


class TransferRequestSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)

    class Meta:
        model = TransferRequest
        fields = [
            "id", "asset", "asset_tag",
            "from_employee", "from_department",
            "to_employee", "to_department",
            "status", "requested_by", "approved_by", "reason",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "status", "requested_by", "approved_by", "created_at", "updated_at"]
