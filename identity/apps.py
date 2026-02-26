"""
Identity App configuration.
"""
from django.apps import AppConfig


class IdentityConfig(AppConfig):
    """App config for the Identity bounded context."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "identity"
    verbose_name = "Identity & RBAC"
