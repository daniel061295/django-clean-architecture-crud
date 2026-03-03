"""
Identity Infrastructure Models — Django ORM models for the Identity bounded context.

These models are ONLY used for persistence. Business logic lives in domain entities.
"""
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class PermissionModel(models.Model):
    """
    ORM model for a system permission.

    Maps to the 'identity_permission' table.
    """

    code = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        db_table = "identity_permission"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"

    def __str__(self) -> str:
        return self.code


class RoleModel(models.Model):
    """
    ORM model for a user role.

    Maps to the 'identity_role' table.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    permissions = models.ManyToManyField(
        PermissionModel,
        related_name="roles",
        blank=True,
    )

    class Meta:
        db_table = "identity_role"
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self) -> str:
        return self.name


class CustomUserModel(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.

    Uses UUID as primary key and email as the login identifier.
    Maps to the 'identity_user' table.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=150,
        unique=False,
        blank=True,
    )
    roles = models.ManyToManyField(
        RoleModel,
        related_name="users",
        blank=True,
    )
    avatar = models.TextField(
        blank=True,
        default="",
        help_text="User profile avatar as base64 encoded string.",
    )
    auth_provider = models.CharField(
        max_length=50,
        default="local",
        help_text="Provider used to authenticate ('local', 'google', etc.)."
    )

    USERNAME_FIELD = "email"
    # Remove email from REQUIRED_FIELDS since it's the USERNAME_FIELD
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "identity_user"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email
