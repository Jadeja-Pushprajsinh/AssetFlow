from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class DashboardKPIView(APIView):
    """Return a zeroed KPI payload for the dashboard shell."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "assets": {
                    "available": 0,
                    "allocated": 0,
                    "under_maintenance": 0,
                },
                "active_bookings": 0,
                "pending_transfers": 0,
                "upcoming_returns": 0,
                "overdue_allocations": 0,
                "maintenance_today": 0,
            }
        )
