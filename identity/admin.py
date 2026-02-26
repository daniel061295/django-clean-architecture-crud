"""
Identity Admin — Register models with Django admin site.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from identity.infrastructure.models import CustomUserModel, PermissionModel, RoleModel


@admin.register(PermissionModel)
class PermissionAdmin(admin.ModelAdmin):
    """Admin for system permissions."""

    list_display = ("code", "description")
    search_fields = ("code",)


@admin.register(RoleModel)
class RoleAdmin(admin.ModelAdmin):
    """Admin for system roles."""

    list_display = ("name",)
    filter_horizontal = ("permissions",)
    search_fields = ("name",)


@admin.register(CustomUserModel)
class CustomUserAdmin(UserAdmin):
    """Admin for custom user model."""

    model = CustomUserModel
    list_display = ("email", "username", "is_staff", "is_active")
    list_filter = ("is_staff", "is_active")
    filter_horizontal = ("roles", "groups", "user_permissions")
    fieldsets = UserAdmin.fieldsets + (
        ("Roles", {"fields": ("roles",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "roles"),
            },
        ),
    )
    search_fields = ("email", "username")
    ordering = ("email",)
