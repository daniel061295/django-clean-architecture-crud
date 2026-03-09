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




from ._helpers import _plan_to_dto, _subscription_to_dto

class GetMySubscription:
    """
    Returns the current subscription status plus today's usage for a user.

    This powers the GET /billing/me endpoint.
    """

    @inject
    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
        daily_usage_repository: DailyUsageRepository,
    ) -> None:
        self._sub_repo = subscription_repository
        self._plan_repo = plan_repository
        self._usage_repo = daily_usage_repository

    def execute(self, user_id: UUID) -> MySubscriptionOutputDTO:
        """
        Fetches a composite view: plan name, subscription status, and today's usage.

        Args:
            user_id: UUID of the requesting user.

        Returns:
            MySubscriptionOutputDTO: The composite subscription status.

        Raises:
            NoActiveSubscriptionError: If the user has no active subscription.
            PlanNotFoundError: If the referenced plan no longer exists.
        """
        subscription = self._sub_repo.get_active_by_user(user_id)
        if subscription is None:
            raise NoActiveSubscriptionError("No active subscription found for this user.")

        plan = self._plan_repo.get_by_id(subscription.plan_id)
        if plan is None:
            raise PlanNotFoundError(f"Plan {subscription.plan_id} not found.")

        usage = self._usage_repo.get_or_create(user_id, date.today())

        return MySubscriptionOutputDTO(
            plan_name=plan.name,
            plan_id=str(plan.id),
            status=subscription.status.value,
            scan_limit_per_day=plan.scan_limit_per_day,
            ads_enabled=plan.ads_enabled,
            usage_today=usage.scans_count,
            features=plan.features,
        )

