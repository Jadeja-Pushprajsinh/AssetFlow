"""
notifications.services
-----------------------
Shared helpers for writing ActivityLog entries and creating Notifications.
Import this in any app's serializer or view — it's the single place all
activity logging goes through.
"""
from apps.notifications.models import ActivityLog, Notification, NotificationType


def log_activity(user, action, entity_type, entity_id, details=None, request=None):
    """
    Write an immutable ActivityLog entry.

    Usage:
        from apps.notifications.services import log_activity
        log_activity(
            user=request.user,
            action="asset.allocated",
            entity_type="Asset",
            entity_id=asset.id,
            details={"asset_tag": asset.asset_tag, "allocated_to": employee.email},
            request=request,
        )
    """
    ip = None
    if request:
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR")

    ActivityLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
        ip_address=ip,
    )


def notify_user(user, notification_type, message, entity_type=None, entity_id=None):
    """
    Create an in-app Notification for a user.

    Usage:
        from apps.notifications.services import notify_user
        notify_user(
            user=employee,
            notification_type=NotificationType.ALLOCATION,
            message="A new asset has been allocated to you.",
            entity_type="Allocation",
            entity_id=allocation.id,
        )
    """
    Notification.objects.create(
        user=user,
        type=notification_type,
        message=message,
        entity_type=entity_type,
        entity_id=entity_id,
    )


def notify_users(users, notification_type, message, entity_type=None, entity_id=None):
    """Bulk-notify multiple users (e.g. all auditors in a cycle)."""
    Notification.objects.bulk_create([
        Notification(
            user=u,
            type=notification_type,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        for u in users
    ])
