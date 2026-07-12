from django.db import models
from django.db import transaction


class Allocation(models.Model):
    HOLDER_TYPE_CHOICES = [
        ('employee', 'Employee'),
        ('department', 'Department'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('transferred', 'Transferred'),
    ]

    asset = models.ForeignKey('assets.Asset', on_delete=models.PROTECT, related_name='allocations')
    holder_type = models.CharField(max_length=20, choices=HOLDER_TYPE_CHOICES)
    holder_employee = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='allocations',
    )
    holder_department = models.ForeignKey(
        'org.Department',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='allocations',
    )
    allocated_date = models.DateField()
    expected_return_date = models.DateField(null=True, blank=True)
    actual_return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    return_notes = models.TextField(blank=True, null=True)
    allocated_by = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='performed_allocations',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['asset', 'status']),
            models.Index(fields=['expected_return_date']),
            models.Index(fields=['holder_employee', 'status']),
        ]

    def __str__(self):
        return f"Allocation {self.id} — {self.asset.asset_tag} ({self.status})"


class TransferRequest(models.Model):
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    asset = models.ForeignKey('assets.Asset', on_delete=models.PROTECT, related_name='transfers')
    # From-holder
    from_employee = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transfers_from',
    )
    from_department = models.ForeignKey(
        'org.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transfers_from',
    )
    # To-holder
    to_employee = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transfers_to',
    )
    to_department = models.ForeignKey(
        'org.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transfers_to',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    requested_by = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='transfer_requests_made',
    )
    approved_by = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_transfers',
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['asset', 'status']),
        ]

    def __str__(self):
        return f"Transfer {self.id} — {self.asset.asset_tag} ({self.status})"
