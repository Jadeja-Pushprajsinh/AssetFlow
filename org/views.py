from rest_framework import viewsets
from .models import Department, AssetCategory
from .serializers import DepartmentSerializer, AssetCategorySerializer
from accounts.permissions import IsAdminOrAssetManager, IsEmployee


class DepartmentViewSet(viewsets.ModelViewSet):
    """
    GET  (list/retrieve) — any authenticated Employee
    POST/PUT/PATCH/DELETE — Admin or Asset Manager only
    """
    queryset = Department.objects.select_related('head__user', 'parent_department').prefetch_related('sub_departments').all()
    serializer_class = DepartmentSerializer
    filterset_fields = ['is_active', 'parent_department']
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsEmployee()]
        return [IsAdminOrAssetManager()]


class AssetCategoryViewSet(viewsets.ModelViewSet):
    """
    GET  — any authenticated Employee
    Writes — Admin or Asset Manager only
    """
    queryset = AssetCategory.objects.all()
    serializer_class = AssetCategorySerializer
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsEmployee()]
        return [IsAdminOrAssetManager()]
