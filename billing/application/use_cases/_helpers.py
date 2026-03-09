"""
Billing Application Use Cases — Business orchestration for SaaS billing.

Each class handles a single, specific business action following the Command Pattern.
"""
from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import UUID

from injector import inject

from billing.application.dtos import (
    AuthorizePlantScanOutputDTO,
    CancelSubscriptionInputDTO,
    ChangePlanInputDTO,
    CheckDailyScanLimitInputDTO,
    CheckDailyScanLimitOutputDTO,
    CheckSubscriptionStatusInputDTO,
    CheckSubscriptionStatusOutputDTO,
    CreateFreeSubscriptionForUserInputDTO,
    CreatePlanInputDTO,
    CreateSubscriptionInputDTO,
    MySubscriptionOutputDTO,
    PlanOutputDTO,
    SubscriptionOutputDTO,
)
from billing.domain.entities import Plan, Subscription
from billing.domain.exceptions import (
    NoActiveSubscriptionError,
    PlanAlreadyExistsError,
    PlanNotFoundError,
    SubscriptionAlreadyExistsError,
)
from billing.domain.interfaces import DailyUsageRepository, PlanRepository, SubscriptionRepository
from billing.domain.value_objects import SubscriptionStatus

def _plan_to_dto(plan: Plan) -> PlanOutputDTO:
    return PlanOutputDTO(
        id=str(plan.id),
        name=plan.name,
        price=plan.price,
        scan_limit_per_day=plan.scan_limit_per_day,
        ads_enabled=plan.ads_enabled,
        features=plan.features,
        is_active=plan.is_active,
    )

def _subscription_to_dto(sub: Subscription) -> SubscriptionOutputDTO:
    return SubscriptionOutputDTO(
        id=str(sub.id),
        user_id=str(sub.user_id),
        plan_id=str(sub.plan_id),
        status=sub.status.value,
        start_date=sub.start_date.isoformat(),
        end_date=sub.end_date.isoformat() if sub.end_date else None,
        external_id=sub.external_id,
    )
