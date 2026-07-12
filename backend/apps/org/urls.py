from django.urls import path
from apps.org import views

urlpatterns = [
    path("departments/",          views.DepartmentListCreateView.as_view(),  name="department_list"),
    path("departments/<int:pk>/", views.DepartmentDetailView.as_view(),      name="department_detail"),
    path("categories/",           views.AssetCategoryListCreateView.as_view(), name="category_list"),
    path("categories/<int:pk>/",  views.AssetCategoryDetailView.as_view(),   name="category_detail"),
]
