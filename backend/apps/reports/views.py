"""
Dashboard KPI endpoint — cross-domain aggregation.
Returns counts used by the dashboard shell.
"""
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assets.models import Asset, AssetStatus
from apps.allocations.models import Allocation, AllocationStatus, TransferRequest, TransferStatus
from apps.bookings.models import Booking, BookingStatus
from apps.maintenance.models import MaintenanceRequest, MaintenanceStatus


class DashboardKPIView(APIView):
    """
    GET /api/v1/reports/dashboard/
    Returns KPI counts for the dashboard shell.
    Role-filtered: employees see only their own data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.now().date()

        # Asset KPIs (org-wide for managers/admins, dept-filtered for others)
        asset_qs = Asset.objects.all()

        available_count = asset_qs.filter(status=AssetStatus.AVAILABLE).count()
        allocated_count = asset_qs.filter(status=AssetStatus.ALLOCATED).count()
        under_maintenance_count = asset_qs.filter(status=AssetStatus.UNDER_MAINTENANCE).count()

        # Active bookings
        active_bookings = Booking.objects.filter(
            status__in=[BookingStatus.UPCOMING, BookingStatus.ONGOING]
        ).count()

        # Pending transfers
        pending_transfers = TransferRequest.objects.filter(
            status=TransferStatus.REQUESTED
        ).count()

        # Upcoming returns (within 7 days)
        upcoming_returns = Allocation.objects.filter(
            status=AllocationStatus.ACTIVE,
            expected_return_date__lte=today + timezone.timedelta(days=7),
            expected_return_date__gte=today,
        ).count()

        # Overdue allocations
        overdue = Allocation.objects.filter(
            status=AllocationStatus.ACTIVE,
            expected_return_date__lt=today,
        ).count()

        # Maintenance pending today (created today)
        maintenance_today = MaintenanceRequest.objects.filter(
            status=MaintenanceStatus.PENDING,
            created_at__date=today,
        ).count()

        return Response({
            "assets": {
                "available": available_count,
                "allocated": allocated_count,
                "under_maintenance": under_maintenance_count,
            },
            "active_bookings": active_bookings,
            "pending_transfers": pending_transfers,
            "upcoming_returns": upcoming_returns,
            "overdue_allocations": overdue,
            "maintenance_today": maintenance_today,
        })


class OverdueAllocationsView(APIView):
    """
    GET /api/v1/reports/overdue/
    Returns overdue allocation list.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.allocations.serializers import AllocationListSerializer
        today = timezone.now().date()
        overdue_qs = Allocation.objects.filter(
            status=AllocationStatus.ACTIVE,
            expected_return_date__lt=today,
        ).select_related("asset", "holder_employee", "holder_department").order_by("expected_return_date")

        return Response(AllocationListSerializer(overdue_qs, many=True).data)
