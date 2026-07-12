"""
org.views
"""
from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated

from apps.accounts.permissions import IsAdmin, IsAdminOrReadOnly
from apps.org.models import Department, AssetCategory
from apps.org.serializers import DepartmentSerializer, AssetCategorySerializer


class DepartmentListCreateView(generics.ListCreateAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name", "code"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        qs = Department.objects.select_related("parent_department", "head").all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs

    def perform_create(self, serializer):
        serializer.save()
        from apps.notifications.services import log_activity
        log_activity(
            user=self.request.user,
            action="department.created",
            entity_type="Department",
            entity_id=serializer.instance.id,
            details={"name": serializer.instance.name},
            request=self.request,
        )


class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = Department.objects.select_related("parent_department", "head").all()

    def perform_destroy(self, instance):
        # Soft-delete: deactivate instead of hard delete
        instance.is_active = False
        instance.save(update_fields=["is_active", "updated_at"])


class AssetCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["name"]
    ordering = ["name"]

    def get_queryset(self):
        qs = AssetCategory.objects.all()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == "true")
        return qs


class AssetCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssetCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    queryset = AssetCategory.objects.all()

    def perform_destroy(self, instance):
        # Soft-delete categories that may have assets attached
        instance.is_active = False
        instance.save(update_fields=["is_active"])
