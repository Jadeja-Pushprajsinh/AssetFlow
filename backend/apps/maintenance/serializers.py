"""
maintenance.serializers — lightweight stubs for Phase 1 (history view).
Full workflow serializers built in Phase 2.
"""
from rest_framework import serializers
from apps.maintenance.models import MaintenanceRequest


class MaintenanceListSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source="asset.asset_tag", read_only=True)
    raised_by_name = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceRequest
        fields = [
            "id", "asset", "asset_tag", "raised_by", "raised_by_name",
            "issue_description", "priority", "status", "resolved_at", "created_at",
        ]

    def get_raised_by_name(self, obj):
        return obj.raised_by.get_full_name() if obj.raised_by else None
