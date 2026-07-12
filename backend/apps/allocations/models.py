"""
allocations.models
------------------
Allocation, TransferRequest — with double-allocation prevention enforced
in services.py via transaction.atomic() + select_for_update().
"""
from django.db import models


class AllocationStatus(models.TextChoices):
    ACTIVE = "Active", "Active"
    RETURNED = "Returned", "Returned"
    TRANSFERRED = "Transferred", "Transferred"


class HolderType(models.TextChoices):
    EMPLOYEE = "employee", "Employee"
    DEPARTMENT = "department", "Department"


class TransferStatus(models.TextChoices):
    REQUESTED = "Requested", "Requested"
    APPROVED = "Approved", "Approved"
    REJECTED = "Rejected", "Rejected"
    COMPLETED = "Completed", "Completed"


class Allocation(models.Model):
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="allocations"
    )
    holder_type = models.CharField(max_length=20, choices=HolderType.choices)
    holder_employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="allocations",
    )
    holder_department = models.ForeignKey(
        "org.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="allocations",
    )
    allocated_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="allocations_made",
    )
    allocated_date = models.DateField()
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=AllocationStatus.choices, default=AllocationStatus.ACTIVE
    )
    return_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Allocation"
        verbose_name_plural = "Allocations"
        indexes = [
            models.Index(fields=["asset", "status"]),  # double-allocation check
            models.Index(fields=["holder_employee"]),
            models.Index(fields=["holder_department"]),
            models.Index(fields=["expected_return_date"]),  # overdue query
        ]

    def __str__(self):
        return f"Allocation #{self.pk} — {self.asset.asset_tag} ({self.status})"


class TransferRequest(models.Model):
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="transfer_requests"
    )
    from_employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_out",
    )
    from_department = models.ForeignKey(
        "org.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_out",
    )
    to_employee = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_in",
    )
    to_department = models.ForeignKey(
        "org.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfers_in",
    )
    status = models.CharField(
        max_length=20, choices=TransferStatus.choices, default=TransferStatus.REQUESTED
    )
    requested_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="transfer_requests_made",
    )
    approved_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transfer_requests_approved",
    )
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Transfer Request"
        verbose_name_plural = "Transfer Requests"
        indexes = [
            models.Index(fields=["asset", "status"]),
        ]

    def __str__(self):
        return f"Transfer #{self.pk} — {self.asset.asset_tag} ({self.status})"
