"""
Billing Admin — Register billing models with Django admin site.
"""
from django.contrib import admin

from billing.infrastructure.models import DailyUsageModel, PlanModel, SubscriptionModel


@admin.register(PlanModel)
class PlanAdmin(admin.ModelAdmin):
    """Admin for SaaS plans."""

    list_display = ("name", "price", "scan_limit_per_day", "ads_enabled", "is_active")
    list_filter = ("is_active", "ads_enabled")
    search_fields = ("name",)


@admin.register(SubscriptionModel)
class SubscriptionAdmin(admin.ModelAdmin):
    """Admin for user subscriptions."""

    list_display = ("user", "plan", "status", "start_date", "end_date")
    list_filter = ("status",)
    search_fields = ("user__email",)
    raw_id_fields = ("user", "plan")


@admin.register(DailyUsageModel)
class DailyUsageAdmin(admin.ModelAdmin):
    """Admin for daily usage tracking."""

    list_display = ("user", "date", "scans_count", "ads_watched")
    list_filter = ("date",)
    search_fields = ("user__email",)
    raw_id_fields = ("user",)
