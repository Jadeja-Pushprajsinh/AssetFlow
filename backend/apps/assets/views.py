"""
assets.views
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAssetManager, IsAdminOrReadOnly
from apps.assets.models import Asset
from apps.assets.serializers import AssetListSerializer, AssetDetailSerializer
from apps.allocations.models import Allocation, AllocationStatus
from apps.maintenance.models import MaintenanceRequest


class AssetListCreateView(generics.ListCreateAPIView):
    search_fields = ["asset_tag", "serial_number", "name", "location"]
    ordering_fields = ["asset_tag", "name", "status", "created_at", "acquisition_date"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return AssetDetailSerializer
        return AssetListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAssetManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Asset.objects.select_related("category", "created_by").all()
        params = self.request.query_params
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("category"):
            qs = qs.filter(category_id=params["category"])
        if params.get("location"):
            qs = qs.filter(location__icontains=params["location"])
        if params.get("is_bookable"):
            qs = qs.filter(is_bookable=params["is_bookable"].lower() == "true")
        return qs


class AssetDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.select_related("category", "created_by").all()
    serializer_class = AssetDetailSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAssetManager()]
        return [IsAuthenticated()]

    def perform_destroy(self, instance):
        # Hard delete is not allowed if allocations exist — PROTECT FK handles this.
        # Soft retirement is preferred.
        instance.status = "Disposed"
        instance.save(update_fields=["status", "updated_at"])

        from apps.notifications.services import log_activity
        log_activity(
            user=self.request.user,
            action="asset.disposed",
            entity_type="Asset",
            entity_id=instance.id,
            details={"asset_tag": instance.asset_tag},
            request=self.request,
        )


class AssetHistoryView(APIView):
    """
    GET /api/v1/assets/{id}/history/
    Returns allocation + maintenance history for an asset.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            asset = Asset.objects.get(pk=pk)
        except Asset.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        from apps.allocations.serializers import AllocationListSerializer
        from apps.maintenance.serializers import MaintenanceListSerializer

        allocations = Allocation.objects.filter(asset=asset).order_by("-created_at")
        maintenance = MaintenanceRequest.objects.filter(asset=asset).order_by("-created_at")

        return Response({
            "asset_tag": asset.asset_tag,
            "allocations": AllocationListSerializer(allocations, many=True).data,
            "maintenance_requests": MaintenanceListSerializer(maintenance, many=True).data,
        })
