from django.urls import path
from apps.allocations import views

urlpatterns = [
    path("",                        views.AllocationListCreateView.as_view(),  name="allocation_list"),
    path("<int:pk>/return/",        views.AllocationReturnView.as_view(),       name="allocation_return"),
    path("transfers/",              views.TransferRequestListCreateView.as_view(), name="transfer_list"),
    path("transfers/<int:pk>/",     views.TransferRequestDetailView.as_view(),  name="transfer_detail"),
]
