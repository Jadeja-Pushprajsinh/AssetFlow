"""
org.models
----------
Department (with self-referential parent hierarchy) and AssetCategory.
"""
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    # FK to Employee defined as string ref to avoid circular import;
    # 'accounts.Employee' resolves at runtime.
    head = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["parent_department"]),
        ]

    def __str__(self):
        return self.name


class AssetCategory(models.Model):
    """
    custom_fields stores the SCHEMA — a list of field definitions:
    [{"name": "warranty_years", "type": "integer", "required": false}, ...]
    Actual values per asset are stored in Asset.custom_field_values.
    """
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    custom_fields = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asset Category"
        verbose_name_plural = "Asset Categories"

    def __str__(self):
        return self.name
