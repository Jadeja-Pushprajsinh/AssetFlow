from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import Employee


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    list_display = ["employee_id", "email", "first_name", "last_name", "role", "status", "department"]
    list_filter = ["role", "status", "department"]
    search_fields = ["email", "first_name", "last_name", "employee_id"]
    ordering = ["email"]

    fieldsets = UserAdmin.fieldsets + (
        ("AssetFlow", {"fields": ("employee_id", "phone", "avatar", "role", "status", "department")}),
    )
    readonly_fields = ["employee_id", "created_at", "updated_at"]
