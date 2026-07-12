from django.db import models
from django.utils import timezone


class Booking(models.Model):
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    asset = models.ForeignKey('assets.Asset', on_delete=models.PROTECT, related_name='bookings')
    booked_by = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, related_name='bookings'
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming', db_index=True)
    purpose = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            # Compound index for overlap query: asset + time range
            models.Index(fields=['asset', 'start_time', 'end_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Booking {self.id} — {self.asset.asset_tag} [{self.start_time} → {self.end_time}]"

    @property
    def computed_status(self):
        """Status derived from current time vs slot. Only 'cancelled' uses stored value."""
        if self.status == 'cancelled':
            return 'cancelled'
        now = timezone.now()
        if now < self.start_time:
            return 'upcoming'
        if self.start_time <= now <= self.end_time:
            return 'ongoing'
        return 'completed'
