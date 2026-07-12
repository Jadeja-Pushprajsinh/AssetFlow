from django.urls import path
from apps.assets import views

urlpatterns = [
    path("",          views.AssetListCreateView.as_view(), name="asset_list"),
    path("<int:pk>/", views.AssetDetailView.as_view(),    name="asset_detail"),
    path("<int:pk>/history/", views.AssetHistoryView.as_view(), name="asset_history"),
]
