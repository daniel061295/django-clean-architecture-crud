"""
Billing Infrastructure Repositories — Django ORM implementations of billing domain interfaces.
"""
from datetime import date
from typing import List, Optional
from uuid import UUID

from django.db import transaction

from billing.domain.entities import DailyUsage, Plan, Subscription
from billing.domain.interfaces import DailyUsageRepository, PlanRepository, SubscriptionRepository
from billing.domain.value_objects import SubscriptionStatus
from billing.infrastructure.mappers import DailyUsageMapper, PlanMapper, SubscriptionMapper
from billing.infrastructure.models import DailyUsageModel, PlanModel, SubscriptionModel


class DjangoPlanRepository(PlanRepository):
    """Django ORM implementation of PlanRepository."""

    def save(self, plan: Plan) -> Plan:
        """Creates or updates a plan."""
        model, _ = PlanModel.objects.update_or_create(
            id=plan.id,
            defaults={
                "name": plan.name,
                "price": plan.price,
                "scan_limit_per_day": plan.scan_limit_per_day,
                "ads_enabled": plan.ads_enabled,
                "features": plan.features,
                "is_active": plan.is_active,
            },
        )
        return PlanMapper.to_domain(model)

    def get_by_id(self, plan_id: UUID) -> Optional[Plan]:
        """Retrieves a plan by UUID."""
        try:
            return PlanMapper.to_domain(PlanModel.objects.get(id=plan_id))
        except PlanModel.DoesNotExist:
            return None

    def list_active(self) -> List[Plan]:
        """Returns all active plans."""
        return [PlanMapper.to_domain(m) for m in PlanModel.objects.filter(is_active=True)]

    def list_all(self) -> List[Plan]:
        """Returns all plans."""
        return [PlanMapper.to_domain(m) for m in PlanModel.objects.all()]


class DjangoSubscriptionRepository(SubscriptionRepository):
    """Django ORM implementation of SubscriptionRepository."""

    def save(self, subscription: Subscription) -> Subscription:
        """Creates or updates a subscription."""
        model, _ = SubscriptionModel.objects.update_or_create(
            id=subscription.id,
            defaults={
                "user_id": subscription.user_id,
                "plan_id": subscription.plan_id,
                "status": subscription.status.value,
                "start_date": subscription.start_date,
                "end_date": subscription.end_date,
                "external_id": subscription.external_id,
            },
        )
        return SubscriptionMapper.to_domain(model)

    def get_by_id(self, subscription_id: UUID) -> Optional[Subscription]:
        """Retrieves a subscription by UUID."""
        try:
            return SubscriptionMapper.to_domain(SubscriptionModel.objects.get(id=subscription_id))
        except SubscriptionModel.DoesNotExist:
            return None

    def get_active_by_user(self, user_id: UUID) -> Optional[Subscription]:
        """Returns the active or trialing subscription for a user."""
        active_statuses = [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value]
        try:
            model = SubscriptionModel.objects.filter(
                user_id=user_id, status__in=active_statuses
            ).latest("start_date")
            return SubscriptionMapper.to_domain(model)
        except SubscriptionModel.DoesNotExist:
            return None

    def cancel_active_by_user(self, user_id: UUID) -> None:
        """Cancels all active subscriptions for a given user."""
        active_statuses = [SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value]
        SubscriptionModel.objects.filter(
            user_id=user_id, status__in=active_statuses
        ).update(status=SubscriptionStatus.CANCELED.value)


class DjangoDailyUsageRepository(DailyUsageRepository):
    """Django ORM implementation of DailyUsageRepository."""

    def save(self, usage: DailyUsage) -> DailyUsage:
        """Persists the current state of a DailyUsage entity."""
        model, _ = DailyUsageModel.objects.update_or_create(
            id=usage.id,
            defaults={
                "user_id": usage.user_id,
                "date": usage.date,
                "scans_count": usage.scans_count,
                "ads_watched": usage.ads_watched,
            },
        )
        return DailyUsageMapper.to_domain(model)

    @transaction.atomic
    def get_or_create(self, user_id: UUID, usage_date: date) -> DailyUsage:
        """
        Atomically retrieves or creates a DailyUsage for the user and date.

        The transaction ensures that concurrent requests do not create
        duplicate records for the same (user, date) pair.
        """
        model, _ = DailyUsageModel.objects.get_or_create(
            user_id=user_id,
            date=usage_date,
            defaults={"scans_count": 0, "ads_watched": 0},
        )
        return DailyUsageMapper.to_domain(model)
