from django.db import models


class MaintenanceRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]

    # Allowed state-machine transitions (server-side enforced)
    ALLOWED_TRANSITIONS = {
        'pending': ['approved', 'rejected'],
        'approved': ['assigned'],
        'assigned': ['in_progress'],
        'in_progress': ['resolved'],
        'rejected': [],
        'resolved': [],
    }

    asset = models.ForeignKey(
        'assets.Asset', on_delete=models.PROTECT, related_name='maintenance_requests'
    )
    raised_by = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True,
        related_name='raised_maintenance',
    )
    issue_description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    photo = models.ImageField(upload_to='maintenance/photos/', null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', db_index=True)
    approved_by = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_maintenance',
    )
    technician = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_maintenance',
    )
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['asset', 'status']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"MR-{self.id} — {self.asset.asset_tag} ({self.status})"
