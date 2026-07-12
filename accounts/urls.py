from django.urls import path
from .views import (
    SignupView,
    LoginView,
    TokenRefreshAPIView,
    MeView,
    EmployeeListView,
    EmployeeDetailView,
    RolePromotionView,
    ForgotPasswordView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='auth-signup'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('token/refresh/', TokenRefreshAPIView.as_view(), name='auth-token-refresh'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='auth-forgot-password'),
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/promote/', RolePromotionView.as_view(), name='employee-promote'),
]
