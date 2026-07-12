"""
notifications.models
--------------------
Notification — in-app only (polling via React Query).
ActivityLog — immutable audit trail of every significant action.
"""
from django.db import models


class NotificationType(models.TextChoices):
    ALLOCATION = "allocation", "Allocation"
    TRANSFER = "transfer", "Transfer"
    BOOKING = "booking", "Booking"
    MAINTENANCE = "maintenance", "Maintenance"
    AUDIT = "audit", "Audit"
    SYSTEM = "system", "System"


class Notification(models.Model):
    user = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=30, choices=NotificationType.choices)
    message = models.TextField()
    entity_type = models.CharField(max_length=50, blank=True, null=True)
    entity_id = models.PositiveIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        indexes = [
            models.Index(fields=["user", "is_read"]),   # unread badge count
            models.Index(fields=["user", "created_at"]), # notification list pagination
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Notif → {self.user.email}: {self.message[:60]}"


class ActivityLog(models.Model):
    """
    Immutable audit trail. No updated_at — these records are never modified.
    """
    user = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="activity_logs",
    )  # null if system-generated action
    action = models.CharField(max_length=100)        # e.g. "asset.allocated"
    entity_type = models.CharField(max_length=50)   # e.g. "Asset"
    entity_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)  # before/after snapshot
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        indexes = [
            models.Index(fields=["entity_type", "entity_id"]), # per-entity history
            models.Index(fields=["user", "timestamp"]),         # user activity view
            models.Index(fields=["timestamp"]),                 # org-wide feed DESC
        ]
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} by {self.user} at {self.timestamp:%Y-%m-%d %H:%M}"
