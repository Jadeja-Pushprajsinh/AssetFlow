from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class DashboardKPIViewTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="dashboard-user",
            password="test-pass-123",
        )

    def test_dashboard_returns_zeroed_payload(self):
        self.client.force_authenticate(self.user)

        response = self.client.get("/api/v1/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
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
            },
        )
