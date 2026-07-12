from rest_framework import serializers
from .models import Department, AssetCategory


class DepartmentSerializer(serializers.ModelSerializer):
    sub_departments = serializers.SerializerMethodField()
    head_name = serializers.CharField(source='head.full_name', read_only=True, default=None)
    parent_department_name = serializers.CharField(
        source='parent_department.name', read_only=True, default=None
    )

    class Meta:
        model = Department
        fields = (
            'id', 'name', 'parent_department', 'parent_department_name',
            'head', 'head_name', 'is_active', 'sub_departments',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_sub_departments(self, obj):
        # Shallow list of immediate children — avoid deep recursion
        return [{'id': d.id, 'name': d.name} for d in obj.sub_departments.filter(is_active=True)]


class AssetCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetCategory
        fields = ('id', 'name', 'description', 'custom_fields', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
