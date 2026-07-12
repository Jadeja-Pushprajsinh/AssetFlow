"""
assets.models
-------------
Asset registry — auto-generated asset tags, status state machine.
"""
from django.db import models
from django.db import transaction


class AssetStatus(models.TextChoices):
    AVAILABLE = "Available", "Available"
    ALLOCATED = "Allocated", "Allocated"
    RESERVED = "Reserved", "Reserved"
    UNDER_MAINTENANCE = "Under Maintenance", "Under Maintenance"
    LOST = "Lost", "Lost"
    RETIRED = "Retired", "Retired"
    DISPOSED = "Disposed", "Disposed"


class AssetCondition(models.TextChoices):
    NEW = "New", "New"
    GOOD = "Good", "Good"
    FAIR = "Fair", "Fair"
    POOR = "Poor", "Poor"


class Asset(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(
        "org.AssetCategory", on_delete=models.PROTECT, related_name="assets"
    )
    asset_tag = models.CharField(max_length=20, unique=True, blank=True)
    serial_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    acquisition_date = models.DateField(null=True, blank=True)
    acquisition_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    condition = models.CharField(
        max_length=20, choices=AssetCondition.choices, default=AssetCondition.GOOD
    )
    location = models.CharField(max_length=200)
    is_bookable = models.BooleanField(default=False)
    status = models.CharField(
        max_length=30, choices=AssetStatus.choices, default=AssetStatus.AVAILABLE
    )
    # Stores values for this category's custom_fields schema
    custom_field_values = models.JSONField(default=dict, blank=True)

    photo = models.ImageField(upload_to="assets/photos/", null=True, blank=True)
    documents = models.FileField(
        upload_to="assets/documents/", null=True, blank=True
    )  # Single file for now; migrate to AssetDocument model if multi-file needed

    created_by = models.ForeignKey(
        "accounts.Employee",
        on_delete=models.SET_NULL,
        null=True,
        related_name="assets_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Asset"
        verbose_name_plural = "Assets"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["location"]),
            models.Index(fields=["status", "category"]),
        ]

    def __str__(self):
        return f"{self.asset_tag} — {self.name}"

    def save(self, *args, **kwargs):
        """Auto-generate asset_tag (AF-0001) on first create, with a DB lock
        to prevent duplicates under concurrent inserts."""
        if not self.asset_tag:
            with transaction.atomic():
                last = (
                    Asset.objects.select_for_update()
                    .filter(asset_tag__startswith="AF-")
                    .order_by("-asset_tag")
                    .first()
                )
                if last and last.asset_tag:
                    try:
                        last_num = int(last.asset_tag.split("-")[1])
                    except (IndexError, ValueError):
                        last_num = 0
                else:
                    last_num = 0
                self.asset_tag = f"AF-{last_num + 1:04d}"
        super().save(*args, **kwargs)


# ── Allowed status transitions (enforced in serializers/services) ─────────────
ASSET_STATUS_TRANSITIONS = {
    AssetStatus.AVAILABLE: [
        AssetStatus.ALLOCATED,
        AssetStatus.RESERVED,
        AssetStatus.UNDER_MAINTENANCE,
        AssetStatus.RETIRED,
        AssetStatus.DISPOSED,
    ],
    AssetStatus.ALLOCATED: [
        AssetStatus.AVAILABLE,
        AssetStatus.UNDER_MAINTENANCE,  # Option B: freeze allocation
        AssetStatus.RETIRED,
        AssetStatus.DISPOSED,
    ],
    AssetStatus.RESERVED: [
        AssetStatus.AVAILABLE,
        AssetStatus.UNDER_MAINTENANCE,
        AssetStatus.RETIRED,
    ],
    AssetStatus.UNDER_MAINTENANCE: [
        AssetStatus.AVAILABLE,
        AssetStatus.ALLOCATED,  # Resume allocation after maintenance
    ],
    AssetStatus.LOST: [],
    AssetStatus.RETIRED: [AssetStatus.AVAILABLE],
    AssetStatus.DISPOSED: [],
}
