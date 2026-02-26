"""
Identity models — re-exports all Django ORM models from the infrastructure layer.

This file is required by Django's ORM to discover models within the 'identity' app.
Business logic lives in identity/domain/entities.py, not here.
"""
from identity.infrastructure.models import CustomUserModel, PermissionModel, RoleModel

__all__ = ["CustomUserModel", "PermissionModel", "RoleModel"]
