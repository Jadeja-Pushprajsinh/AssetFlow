from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import AuditCycle, AuditItem
from .serializers import AuditCycleSerializer, AuditItemSerializer
from accounts.permissions import IsAssetManager, IsEmployee
from assets.models import Asset


class AuditCycleViewSet(viewsets.ModelViewSet):
    serializer_class = AuditCycleSerializer
    permission_classes = [IsAssetManager]
    filterset_fields = ['status', 'scope_department']
    ordering = ['-start_date']

    def get_queryset(self):
        return AuditCycle.objects.prefetch_related('auditors', 'items__asset').all()

    @action(detail=True, methods=['post'], url_path='close')
    def close_cycle(self, request, pk=None):
        """
        POST /api/audits/<pk>/close/
        Closing the cycle is the ONLY action that updates asset statuses.
        Missing → Lost (atomic). Damaged items flagged but not auto-changed.
        """
        cycle = self.get_object()
        if cycle.status != 'active':
            return Response({'detail': 'Only active cycles can be closed.'}, status=400)

        with transaction.atomic():
            missing_asset_ids = cycle.items.filter(result='missing').values_list('asset_id', flat=True)
            Asset.objects.filter(pk__in=missing_asset_ids).update(status='lost')
            cycle.status = 'closed'
            cycle.save()

        return Response(AuditCycleSerializer(cycle).data)


class AuditItemViewSet(viewsets.ModelViewSet):
    serializer_class = AuditItemSerializer
    permission_classes = [IsEmployee]
    filterset_fields = ['audit_cycle', 'result']

    def get_queryset(self):
        return AuditItem.objects.select_related('asset', 'audited_by__user', 'audit_cycle').all()
