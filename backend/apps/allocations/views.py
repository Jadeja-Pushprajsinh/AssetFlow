"""
allocations.views
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAssetManager
from apps.allocations.models import Allocation, TransferRequest, AllocationStatus
from apps.allocations.serializers import (
    AllocationListSerializer,
    AllocationCreateSerializer,
    AllocationReturnSerializer,
    TransferRequestSerializer,
)
from apps.allocations.services import return_allocation


class AllocationListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == "POST":
            return AllocationCreateSerializer
        return AllocationListSerializer

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAssetManager()]
        return [IsAuthenticated()]

    def get_queryset(self):
        qs = Allocation.objects.select_related(
            "asset", "holder_employee", "holder_department", "allocated_by"
        )
        user = self.request.user
        # Non-managers see only their own allocations
        if user.role == "employee":
            qs = qs.filter(holder_employee=user)
        params = self.request.query_params
        if params.get("status"):
            qs = qs.filter(status=params["status"])
        if params.get("asset"):
            qs = qs.filter(asset_id=params["asset"])
        return qs.order_by("-created_at")


class AllocationReturnView(APIView):
    """POST /api/v1/allocations/{id}/return/"""
    permission_classes = [IsAssetManager]

    def post(self, request, pk):
        try:
            allocation = Allocation.objects.get(pk=pk, status=AllocationStatus.ACTIVE)
        except Allocation.DoesNotExist:
            return Response({"detail": "Active allocation not found."}, status=404)

        serializer = AllocationReturnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        allocation = return_allocation(
            allocation=allocation,
            returned_by=request.user,
            return_notes=serializer.validated_data.get("return_notes", ""),
            new_condition=serializer.validated_data.get("condition"),
        )

        from apps.notifications.services import log_activity
        log_activity(
            user=request.user,
            action="asset.returned",
            entity_type="Allocation",
            entity_id=allocation.id,
            details={"asset_tag": allocation.asset.asset_tag},
            request=request,
        )
        return Response(AllocationListSerializer(allocation).data)


class TransferRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = TransferRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TransferRequest.objects.select_related(
            "asset", "requested_by", "approved_by"
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)


class TransferRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = TransferRequestSerializer
    permission_classes = [IsAssetManager]
    queryset = TransferRequest.objects.select_related("asset").all()
