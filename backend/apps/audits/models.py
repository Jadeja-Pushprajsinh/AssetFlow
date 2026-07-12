"""
audits.models
-------------
AuditCycle + AuditItem.

IMPORTANT: Asset status changes (e.g. → Lost) happen ONLY when the AuditCycle
is Closed, not when an AuditItem is marked Missing. This is enforced in
audits/services.py::close_audit_cycle().
"""
from django.db import models


class AuditCycleStatus(models.TextChoices):
    DRAFT = "Draft", "Draft"
    ACTIVE = "Active", "Active"
    COMPLETED = "Completed", "Completed"
    CLOSED = "Closed", "Closed"


class AuditItemResult(models.TextChoices):
    PENDING = "Pending", "Pending"
    VERIFIED = "Verified", "Verified"
    MISSING = "Missing", "Missing"
    DAMAGED = "Damaged", "Damaged"


class AuditCycle(models.Model):
    name = models.CharField(max_length=200)
    scope_department = models.ForeignKey(
        "org.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_cycles",
    )  # null = org-wide
    scope_location = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20, choices=AuditCycleStatus.choices, default=AuditCycleStatus.DRAFT
    )
    auditors = models.ManyToManyField(
        "accounts.Employee", related_name="audit_cycles", blank=True
    )
    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_cycles_created",
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_cycles_closed",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Audit Cycle"
        verbose_name_plural = "Audit Cycles"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["scope_department"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"


class AuditItem(models.Model):
    audit_cycle = models.ForeignKey(
        AuditCycle, on_delete=models.CASCADE, related_name="items"
    )
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="audit_items"
    )
    result = models.CharField(
        max_length=20, choices=AuditItemResult.choices, default=AuditItemResult.PENDING
    )
    notes = models.TextField(blank=True, null=True)
    audited_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_items",
    )
    audited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Audit Item"
        verbose_name_plural = "Audit Items"
        unique_together = ("audit_cycle", "asset")  # prevent duplicate entries
        indexes = [
            models.Index(fields=["audit_cycle", "result"]),  # discrepancy report
            models.Index(fields=["asset"]),
        ]

    def __str__(self):
        return f"AuditItem {self.asset.asset_tag} in {self.audit_cycle.name}: {self.result}"
