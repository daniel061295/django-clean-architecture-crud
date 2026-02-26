"""
Billing App configuration.
"""
from django.apps import AppConfig


class BillingConfig(AppConfig):
    """App config for the Billing bounded context."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "billing"
    verbose_name = "Billing & Subscriptions"
