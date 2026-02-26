"""
Billing Infrastructure Mappers — Convert between ORM models and Domain entities.
"""
from uuid import UUID

from billing.domain.entities import DailyUsage, Plan, Subscription
from billing.domain.value_objects import SubscriptionStatus
from billing.infrastructure.models import DailyUsageModel, PlanModel, SubscriptionModel


class PlanMapper:
    """Maps between PlanModel (ORM) and Plan (Domain)."""

    @staticmethod
    def to_domain(model: PlanModel) -> Plan:
        """Converts a PlanModel to a domain Plan entity."""
        return Plan(
            id=model.id,
            name=model.name,
            price=model.price,
            scan_limit_per_day=model.scan_limit_per_day,
            ads_enabled=model.ads_enabled,
            features=model.features,
            is_active=model.is_active,
        )

    @staticmethod
    def to_db(plan: Plan) -> PlanModel:
        """Converts a domain Plan to an ORM PlanModel (not saved)."""
        return PlanModel(
            id=plan.id,
            name=plan.name,
            price=plan.price,
            scan_limit_per_day=plan.scan_limit_per_day,
            ads_enabled=plan.ads_enabled,
            features=plan.features,
            is_active=plan.is_active,
        )


class SubscriptionMapper:
    """Maps between SubscriptionModel (ORM) and Subscription (Domain)."""

    @staticmethod
    def to_domain(model: SubscriptionModel) -> Subscription:
        """Converts a SubscriptionModel to a domain Subscription entity."""
        return Subscription(
            id=model.id,
            user_id=model.user_id,
            plan_id=model.plan_id,
            status=SubscriptionStatus(model.status),
            start_date=model.start_date,
            end_date=model.end_date,
            external_id=model.external_id,
        )


class DailyUsageMapper:
    """Maps between DailyUsageModel (ORM) and DailyUsage (Domain)."""

    @staticmethod
    def to_domain(model: DailyUsageModel) -> DailyUsage:
        """Converts a DailyUsageModel to a domain DailyUsage entity."""
        return DailyUsage(
            id=model.id,
            user_id=model.user_id,
            date=model.date,
            scans_count=model.scans_count,
            ads_watched=model.ads_watched,
        )
