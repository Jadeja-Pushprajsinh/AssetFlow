from rest_framework import serializers
from django.db import transaction
from .models import AuditCycle, AuditItem
from assets.models import Asset


class AuditItemSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.asset_tag', read_only=True)
    audited_by_name = serializers.CharField(source='audited_by.full_name', read_only=True, default=None)

    class Meta:
        model = AuditItem
        fields = ('id', 'audit_cycle', 'asset', 'asset_tag', 'result', 'notes',
                  'audited_by', 'audited_by_name', 'audited_at', 'created_at')
        read_only_fields = ('id', 'created_at', 'audited_by')


class AuditCycleSerializer(serializers.ModelSerializer):
    items = AuditItemSerializer(many=True, read_only=True)
    auditor_count = serializers.SerializerMethodField()
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, default=None)

    class Meta:
        model = AuditCycle
        fields = ('id', 'name', 'scope_department', 'scope_location',
                  'start_date', 'end_date', 'status', 'auditors',
                  'created_by', 'created_by_name', 'auditor_count',
                  'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'status', 'created_by', 'created_at', 'updated_at')

    def get_auditor_count(self, obj):
        return obj.auditors.count()

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee'):
            validated_data['created_by'] = request.user.employee
        return super().create(validated_data)
