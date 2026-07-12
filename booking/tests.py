from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import Employee
from assets.models import Asset
from org.models import AssetCategory, Department
from .models import Booking


class BookingLifecycleTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='booker', password='test-pass-123')
        self.department = Department.objects.create(name='Operations')
        self.employee = Employee.objects.create(
            user=self.user,
            department=self.department,
            role='employee',
        )
        self.category = AssetCategory.objects.create(name='Room')
        self.asset = Asset.objects.create(
            name='Conference Room',
            category=self.category,
            is_bookable=True,
            status='available',
        )
        self.base_start = timezone.now() + timedelta(days=1, hours=1)
        self.base_end = self.base_start + timedelta(hours=1)
        self.booking = Booking.objects.create(
            asset=self.asset,
            booked_by=self.employee,
            start_time=self.base_start,
            end_time=self.base_end,
            status='upcoming',
            purpose='Standup',
        )
        self.client.force_authenticate(self.user)

    def test_create_booking_rejects_overlap(self):
        response = self.client.post(
            '/api/bookings/',
            {
                'asset': self.asset.id,
                'start_time': self.base_start + timedelta(minutes=30),
                'end_time': self.base_end + timedelta(minutes=30),
                'purpose': 'Conflict',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('already booked', response.data['non_field_errors'][0].lower())

    def test_reschedule_updates_booking_and_restores_upcoming_status(self):
        new_start = self.base_start + timedelta(days=1)
        new_end = new_start + timedelta(hours=1)

        response = self.client.patch(
            f'/api/bookings/{self.booking.id}/reschedule/',
            {'start_time': new_start.isoformat(), 'end_time': new_end.isoformat()},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'upcoming')
        self.assertEqual(response.data['start_time'], new_start.isoformat().replace('+00:00', 'Z'))
        self.assertEqual(response.data['end_time'], new_end.isoformat().replace('+00:00', 'Z'))
