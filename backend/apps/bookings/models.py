"""
bookings.models
---------------
Resource booking with strict overlap validation enforced in services.py.
"""
from django.db import models


class BookingStatus(models.TextChoices):
    UPCOMING = "Upcoming", "Upcoming"
    ONGOING = "Ongoing", "Ongoing"
    COMPLETED = "Completed", "Completed"
    CANCELLED = "Cancelled", "Cancelled"


class Booking(models.Model):
    asset = models.ForeignKey(
        "assets.Asset", on_delete=models.PROTECT, related_name="bookings"
    )
    booked_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="bookings",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=BookingStatus.choices, default=BookingStatus.UPCOMING
    )
    purpose = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Booking"
        verbose_name_plural = "Bookings"
        indexes = [
            # Compound index for the Allen interval-overlap query:
            # filter(asset=, status__in=[...], start_time__lt=new_end, end_time__gt=new_start)
            models.Index(fields=["asset", "start_time", "end_time"]),
            models.Index(fields=["booked_by"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Booking #{self.pk} — {self.asset.asset_tag} {self.start_time:%Y-%m-%d %H:%M}"
