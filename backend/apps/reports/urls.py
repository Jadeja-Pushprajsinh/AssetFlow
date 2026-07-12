from django.urls import path
from apps.reports import views

urlpatterns = [
    path("dashboard/", views.DashboardKPIView.as_view(),       name="dashboard_kpi"),
    path("overdue/",   views.OverdueAllocationsView.as_view(), name="overdue_allocations"),
]
