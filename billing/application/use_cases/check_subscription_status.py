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

class CheckSubscriptionStatus:
    """
    Checks if a user has an active subscription.
    
    This use case verifies subscription status without exposing full subscription details.
    """

    @inject
    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
    ) -> None:
        self._sub_repo = subscription_repository
        self._plan_repo = plan_repository

    def execute(self, input_dto: CheckSubscriptionStatusInputDTO) -> CheckSubscriptionStatusOutputDTO:
        """
        Checks if a user has an active subscription.

        Args:
            input_dto: User UUID.

        Returns:
            CheckSubscriptionStatusOutputDTO: Subscription status information.
        """
        subscription = self._sub_repo.get_active_by_user(input_dto.user_id)
        
        if subscription is None or subscription.status != SubscriptionStatus.ACTIVE:
            return CheckSubscriptionStatusOutputDTO(
                has_active_subscription=False,
            )

        plan = self._plan_repo.get_by_id(subscription.plan_id)
        
        return CheckSubscriptionStatusOutputDTO(
            has_active_subscription=True,
            plan_id=str(subscription.plan_id),
            plan_name=plan.name if plan else None,
            status=subscription.status.value,
        )

