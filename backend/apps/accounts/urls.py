"""
accounts.urls
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts import views

urlpatterns = [
    # Auth
    path("signup/",               views.SignupView.as_view(),               name="signup"),
    path("login/",                views.LoginView.as_view(),                name="login"),
    path("logout/",               views.LogoutView.as_view(),               name="logout"),
    path("token/refresh/",        TokenRefreshView.as_view(),               name="token_refresh"),
    path("password/reset/",       views.PasswordResetRequestView.as_view(), name="password_reset"),
    path("password/reset/confirm/", views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),

    # Profile
    path("me/", views.MeView.as_view(), name="me"),

    # Employee directory
    path("employees/",            views.EmployeeListView.as_view(),   name="employee_list"),
    path("employees/<int:pk>/",   views.EmployeeDetailView.as_view(), name="employee_detail"),
    path("employees/<int:pk>/promote/", views.RolePromotionView.as_view(), name="employee_promote"),
]
