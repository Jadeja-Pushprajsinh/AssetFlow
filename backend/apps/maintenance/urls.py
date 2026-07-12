from django.urls import path
from apps.maintenance.views import MaintenancePlaceholderView

urlpatterns = [
    path("", MaintenancePlaceholderView.as_view(), name="maintenance_placeholder"),
]
