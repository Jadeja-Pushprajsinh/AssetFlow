"""
allocations.services
---------------------
Core business logic for allocation and transfer.
The double-allocation prevention lock lives here.
"""
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.allocations.models import Allocation, AllocationStatus
from apps.assets.models import Asset, AssetStatus


def create_allocation(
    asset,
    holder_type,
    allocated_by,
    allocated_date,
    holder_employee=None,
    holder_department=None,
    expected_return_date=None,
):
    """
    Atomically allocate an asset, preventing double-allocation via
    select_for_update() on the asset row.

    Raises ValidationError (409) if the asset is already actively allocated.
    """
    with transaction.atomic():
        # Lock the asset row to serialize concurrent allocation attempts
        locked_asset = Asset.objects.select_for_update().get(pk=asset.pk)

        if locked_asset.status not in (AssetStatus.AVAILABLE,):
            raise ValidationError(
                {
                    "asset": (
                        f"Asset '{locked_asset.asset_tag}' is currently '{locked_asset.status}' "
                        f"and cannot be allocated. "
                        f"If you need to transfer it, use the Transfer Request endpoint."
                    )
                }
            )

        # Belt-and-suspenders: also check active allocation record
        if Allocation.objects.filter(asset=locked_asset, status=AllocationStatus.ACTIVE).exists():
            raise ValidationError(
                {
                    "asset": (
                        f"Asset '{locked_asset.asset_tag}' already has an active allocation. "
                        f"Use the Transfer Request endpoint instead."
                    )
                }
            )

        allocation = Allocation.objects.create(
            asset=locked_asset,
            holder_type=holder_type,
            holder_employee=holder_employee,
            holder_department=holder_department,
            allocated_by=allocated_by,
            allocated_date=allocated_date,
            expected_return_date=expected_return_date,
            status=AllocationStatus.ACTIVE,
        )

        locked_asset.status = AssetStatus.ALLOCATED
        locked_asset.save(update_fields=["status", "updated_at"])

    return allocation


def return_allocation(allocation, returned_by, return_notes="", new_condition=None):
    """
    Return an asset: close the allocation, update asset status to Available.
    """
    with transaction.atomic():
        locked_asset = Asset.objects.select_for_update().get(pk=allocation.asset_id)

        allocation.status = AllocationStatus.RETURNED
        allocation.actual_return_date = timezone.now().date()
        allocation.return_notes = return_notes
        allocation.save(update_fields=["status", "actual_return_date", "return_notes", "updated_at"])

        locked_asset.status = AssetStatus.AVAILABLE
        if new_condition:
            locked_asset.condition = new_condition
        locked_asset.save(update_fields=["status", "condition", "updated_at"])

    return allocation
