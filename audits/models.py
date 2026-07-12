from django.db import models


class AuditCycle(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]

    name = models.CharField(max_length=255)
    scope_department = models.ForeignKey(
        'org.Department', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audit_cycles',
    )
    scope_location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='planned', db_index=True)
    auditors = models.ManyToManyField(
        'accounts.Employee', blank=True, related_name='audit_cycles'
    )
    created_by = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='created_audits',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.status})"


class AuditItem(models.Model):
    RESULT_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('missing', 'Missing'),
        ('damaged', 'Damaged'),
    ]

    audit_cycle = models.ForeignKey(AuditCycle, on_delete=models.CASCADE, related_name='items')
    asset = models.ForeignKey('assets.Asset', on_delete=models.PROTECT, related_name='audit_items')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    audited_by = models.ForeignKey(
        'accounts.Employee', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='audited_items',
    )
    audited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('audit_cycle', 'asset')]
        indexes = [
            models.Index(fields=['audit_cycle', 'result']),
        ]

    def __str__(self):
        return f"AuditItem — {self.asset.asset_tag} [{self.result}]"
