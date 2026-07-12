from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Asset
from .serializers import AssetSerializer, AssetListSerializer
from accounts.permissions import IsAssetManager, IsEmployee


class AssetViewSet(viewsets.ModelViewSet):
    """
    Asset registry CRUD.
    GET (list/retrieve) — any authenticated Employee
    POST/PUT/PATCH — Asset Manager or Admin
    DELETE — Asset Manager or Admin (only Retired/Disposed assets)
    """
    queryset = Asset.objects.select_related('category', 'created_by__user').all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'category', 'condition', 'is_bookable', 'location']
    search_fields = ['name', 'asset_tag', 'serial_number', 'location']
    ordering_fields = ['asset_tag', 'name', 'created_at', 'acquisition_date']
    ordering = ['asset_tag']

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        return AssetSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'history', 'maintenance_history'):
            return [IsEmployee()]
        return [IsAssetManager()]

    def destroy(self, request, *args, **kwargs):
        asset = self.get_object()
        if asset.status not in ('retired', 'disposed'):
            return Response(
                {'detail': 'Only Retired or Disposed assets can be deleted.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='allocation-history')
    def allocation_history(self, request, pk=None):
        """GET /api/assets/<pk>/allocation-history/"""
        from allocations.models import Allocation
        from allocations.serializers import AllocationSerializer
        asset = self.get_object()
        allocations = Allocation.objects.filter(asset=asset).select_related(
            'holder_employee__user', 'holder_department', 'allocated_by__user'
        ).order_by('-created_at')
        serializer = AllocationSerializer(allocations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='maintenance-history')
    def maintenance_history(self, request, pk=None):
        """GET /api/assets/<pk>/maintenance-history/"""
        from maintenance.models import MaintenanceRequest
        from maintenance.serializers import MaintenanceRequestSerializer
        asset = self.get_object()
        requests = MaintenanceRequest.objects.filter(asset=asset).select_related(
            'raised_by__user', 'approved_by__user', 'technician__user'
        ).order_by('-created_at')
        serializer = MaintenanceRequestSerializer(requests, many=True)
        return Response(serializer.data)
