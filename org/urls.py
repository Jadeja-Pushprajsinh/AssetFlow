from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, AssetCategoryViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'categories', AssetCategoryViewSet, basename='asset-category')

urlpatterns = [
    path('', include(router.urls)),
]
