from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer, MaintenanceStatusUpdateSerializer
from accounts.permissions import IsAssetManager, IsEmployee


class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceRequestSerializer
    filterset_fields = ['status', 'priority', 'asset']
    search_fields = ['asset__asset_tag', 'issue_description']
    ordering_fields = ['created_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = MaintenanceRequest.objects.select_related(
            'asset', 'raised_by__user', 'approved_by__user', 'technician__user'
        ).all()
        user = self.request.user
        if not hasattr(user, 'employee'):
            return qs.none()
        emp = user.employee
        if emp.role in ('admin', 'asset_manager'):
            return qs
        return qs.filter(raised_by=emp)

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return [IsEmployee()]
        return [IsAssetManager()]

    @action(detail=True, methods=['patch'], url_path='transition')
    def transition(self, request, pk=None):
        """PATCH /api/maintenance/<pk>/transition/ — advance the state machine."""
        instance = self.get_object()
        serializer = MaintenanceStatusUpdateSerializer(
            data=request.data,
            context={'instance': instance, 'request': request},
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()
        return Response(MaintenanceRequestSerializer(updated).data)
