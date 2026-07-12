"""
maintenance.models
------------------
MaintenanceRequest workflow:
Pending → Approved/Rejected → Assigned → In Progress → Resolved

Asset status side-effects are handled in services.py only:
- Approved  → asset.status = "Under Maintenance"
- Resolved  → asset.status = "Available" (or "Allocated" if allocation frozen)
"""
from django.db import models


class Priority(models.TextChoices):
    LOW = "Low", "Low"
    MEDIUM = "Medium", "Medium"
    HIGH = "High", "High"
    CRITICAL = "Critical", "Critical"


class MaintenanceStatus(models.TextChoices):
    PENDING = "Pending", "Pending"
    APPROVED = "Approved", "Approved"
    REJECTED = "Rejected", "Rejected"
    ASSIGNED = "Assigned", "Assigned"
    IN_PROGRESS = "In Progress", "In Progress"
    RESOLVED = "Resolved", "Resolved"


class MaintenanceRequest(models.Model):
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="maintenance_requests"
    )
    raised_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="maintenance_raised",
    )
    issue_description = models.TextField()
    priority = models.CharField(
        max_length=20, choices=Priority.choices, default=Priority.MEDIUM
    )
    photo = models.ImageField(upload_to="maintenance/photos/", null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=MaintenanceStatus.choices,
        default=MaintenanceStatus.PENDING,
    )
    approved_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_approved",
    )
    technician = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="maintenance_assigned",
    )
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Maintenance Request"
        verbose_name_plural = "Maintenance Requests"
        indexes = [
            models.Index(fields=["asset", "status"]),
            models.Index(fields=["status"]),
            models.Index(fields=["raised_by"]),
        ]

    def __str__(self):
        return f"MR #{self.pk} — {self.asset.asset_tag} ({self.status})"
