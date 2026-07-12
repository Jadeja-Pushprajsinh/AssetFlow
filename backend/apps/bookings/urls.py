from django.urls import path
from apps.bookings.views import BookingsPlaceholderView

urlpatterns = [
    path("", BookingsPlaceholderView.as_view(), name="bookings_placeholder"),
]
