"""
Billing Infrastructure Models — Django ORM models for the Billing bounded context.

These models are ONLY used for persistence. Business logic lives in domain entities.
"""
import uuid

from django.conf import settings
from django.db import models

from billing.domain.value_objects import SubscriptionStatus


class PlanModel(models.Model):
    """ORM model for a SaaS pricing plan. Maps to 'billing_plan' table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    price = models.FloatField(default=0.0)
    scan_limit_per_day = models.IntegerField(null=True, blank=True)
    ads_enabled = models.BooleanField(default=True)
    features = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "billing_plan"
        verbose_name = "Plan"
        verbose_name_plural = "Plans"

    def __str__(self) -> str:
        return self.name


class SubscriptionModel(models.Model):
    """ORM model for a user subscription. Maps to 'billing_subscription' table."""

    STATUS_CHOICES = [(s.value, s.value) for s in SubscriptionStatus]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    plan = models.ForeignKey(PlanModel, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=SubscriptionStatus.ACTIVE.value)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    external_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "billing_subscription"
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"

    def __str__(self) -> str:
        return f"Subscription({self.user_id}, {self.plan.name}, {self.status})"


class DailyUsageModel(models.Model):
    """ORM model for daily scan usage tracking. Maps to 'billing_daily_usage' table."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_usages",
    )
    date = models.DateField()
    scans_count = models.IntegerField(default=0)
    ads_watched = models.IntegerField(default=0)

    class Meta:
        db_table = "billing_daily_usage"
        verbose_name = "Daily Usage"
        verbose_name_plural = "Daily Usages"
        # Enforce one record per user per day at the DB level
        unique_together = ("user", "date")

    def __str__(self) -> str:
        return f"DailyUsage({self.user_id}, {self.date}, scans={self.scans_count})"
