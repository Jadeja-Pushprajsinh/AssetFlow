from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Asset(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('allocated', 'Allocated'),
        ('reserved', 'Reserved'),
        ('under_maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
        ('retired', 'Retired'),
        ('disposed', 'Disposed'),
    ]

    name = models.CharField(max_length=255)
    category = models.ForeignKey(
        'org.AssetCategory',
        on_delete=models.PROTECT,
        related_name='assets',
    )
    # asset_tag is auto-generated via post_save signal: AF-0001, AF-0002, …
    asset_tag = models.CharField(max_length=20, unique=True, blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    acquisition_date = models.DateField(null=True, blank=True)
    acquisition_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, default='new')
    location = models.CharField(max_length=255, blank=True, null=True)
    is_bookable = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        db_index=True,
    )
    # Stores values matching the category's custom_fields schema
    custom_field_values = models.JSONField(default=dict, blank=True)
    photo = models.ImageField(upload_to='assets/photos/', null=True, blank=True)
    documents = models.FileField(upload_to='assets/docs/', null=True, blank=True)
    created_by = models.ForeignKey(
        'accounts.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_assets',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['status', 'category']),
            models.Index(fields=['location']),
        ]
        ordering = ['asset_tag']

    def __str__(self):
        return f"{self.asset_tag} — {self.name}"


# ---------------------------------------------------------------------------
# Post-save signal: assign asset_tag = AF-{id:04d} after first insert
# ---------------------------------------------------------------------------
@receiver(post_save, sender=Asset)
def assign_asset_tag(sender, instance, created, **kwargs):
    if created and not instance.asset_tag:
        instance.asset_tag = f'AF-{instance.pk:04d}'
        Asset.objects.filter(pk=instance.pk).update(asset_tag=instance.asset_tag)
