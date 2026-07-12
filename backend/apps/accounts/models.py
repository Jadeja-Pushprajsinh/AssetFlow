"""
accounts.models
---------------
Employee extends AbstractUser. Email is the USERNAME_FIELD.
Roles are assigned by Admin only — never set at signup.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    ADMIN = "admin", "Admin"
    ASSET_MANAGER = "asset_manager", "Asset Manager"
    DEPARTMENT_HEAD = "department_head", "Department Head"
    EMPLOYEE = "employee", "Employee"


class EmployeeStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    INACTIVE = "inactive", "Inactive"
    SUSPENDED = "suspended", "Suspended"


class Employee(AbstractUser):
    """
    Custom user model. Uses email as the primary identifier.
    'username' field is kept (required by AbstractUser) but authentication
    uses email.
    """

    # Override email to make it unique and required
    email = models.EmailField(unique=True)

    # employee_id is auto-generated on first save (EMP-0001)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)

    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    role = models.CharField(
        max_length=30, choices=Role.choices, default=Role.EMPLOYEE
    )
    status = models.CharField(
        max_length=20, choices=EmployeeStatus.choices, default=EmployeeStatus.ACTIVE
    )

    # FK to Department — defined here as a string ref to avoid circular import
    department = models.ForeignKey(
        "org.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        indexes = [
            models.Index(fields=["role"]),
            models.Index(fields=["department", "role"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def save(self, *args, **kwargs):
        # Auto-generate employee_id on first create
        if not self.employee_id:
            last = (
                Employee.objects.filter(employee_id__startswith="EMP-")
                .order_by("-employee_id")
                .first()
            )
            if last and last.employee_id:
                try:
                    last_num = int(last.employee_id.split("-")[1])
                except (IndexError, ValueError):
                    last_num = 0
            else:
                last_num = 0
            self.employee_id = f"EMP-{last_num + 1:04d}"
        super().save(*args, **kwargs)

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_asset_manager(self):
        return self.role == Role.ASSET_MANAGER

    @property
    def is_department_head(self):
        return self.role == Role.DEPARTMENT_HEAD
