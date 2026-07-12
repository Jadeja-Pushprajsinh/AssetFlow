from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Allocation, TransferRequest
from .serializers import AllocationSerializer, ReturnSerializer, TransferRequestSerializer
from accounts.permissions import IsAssetManager, IsEmployee


class AllocationViewSet(viewsets.ModelViewSet):
    queryset = Allocation.objects.select_related(
        'asset', 'holder_employee__user', 'holder_department', 'allocated_by__user'
    ).all()
    serializer_class = AllocationSerializer
    filterset_fields = ['status', 'asset', 'holder_employee', 'holder_department', 'holder_type']
    search_fields = ['asset__asset_tag', 'asset__name']
    ordering_fields = ['allocated_date', 'expected_return_date', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsEmployee()]
        return [IsAssetManager()]

    def get_queryset(self):
        qs = super().get_queryset()
        # Employees can only see their own allocations unless they are manager+
        user = self.request.user
        if not hasattr(user, 'employee'):
            return qs.none()
        emp = user.employee
        if emp.role in ('admin', 'asset_manager'):
            return qs
        if emp.role == 'department_head':
            return qs.filter(holder_department=emp.department) | qs.filter(holder_employee=emp)
        return qs.filter(holder_employee=emp)

    @action(detail=True, methods=['patch'], url_path='return')
    def process_return(self, request, pk=None):
        """PATCH /api/allocations/<pk>/return/ — return an active allocation."""
        allocation = self.get_object()
        serializer = ReturnSerializer(allocation, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AllocationSerializer(allocation).data)


class TransferRequestViewSet(viewsets.ModelViewSet):
    queryset = TransferRequest.objects.select_related(
        'asset', 'from_employee__user', 'to_employee__user',
        'requested_by__user', 'approved_by__user',
    ).all()
    serializer_class = TransferRequestSerializer
    filterset_fields = ['status', 'asset']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsEmployee()]
        return [IsAssetManager()]

    @action(detail=True, methods=['patch'], url_path='approve')
    def approve(self, request, pk=None):
        """PATCH /api/allocations/transfers/<pk>/approve/"""
        from accounts.permissions import IsAssetManager
        if not IsAssetManager().has_permission(request, self):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)

        transfer = self.get_object()
        if transfer.status != 'requested':
            return Response({'detail': 'Only requested transfers can be approved.'}, status=400)

        transfer.status = 'approved'
        transfer.approved_by = request.user.employee
        transfer.save()
        return Response(TransferRequestSerializer(transfer).data)

    @action(detail=True, methods=['patch'], url_path='reject')
    def reject(self, request, pk=None):
        """PATCH /api/allocations/transfers/<pk>/reject/"""
        transfer = self.get_object()
        if transfer.status != 'requested':
            return Response({'detail': 'Only requested transfers can be rejected.'}, status=400)
        transfer.status = 'rejected'
        transfer.approved_by = request.user.employee
        transfer.save()
        return Response(TransferRequestSerializer(transfer).data)
