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

class ChangePlan:
    """
    Cancels the user's current subscription (if any) and creates a new active one.

    This is the manual plan change flow, to be replaced by Stripe callbacks later.
    """

    @inject
    def __init__(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
    ) -> None:
        self._sub_repo = subscription_repository
        self._plan_repo = plan_repository

    def execute(self, input_dto: ChangePlanInputDTO) -> SubscriptionOutputDTO:
        """
        Changes a user's plan by canceling the current one and starting a new one.

        Args:
            input_dto: User UUID and target Plan UUID.

        Returns:
            SubscriptionOutputDTO: The newly created subscription.

        Raises:
            PlanNotFoundError: If the target plan does not exist or is inactive.
        """
        plan = self._plan_repo.get_by_id(input_dto.plan_id)
        if plan is None or not plan.is_active:
            raise PlanNotFoundError(f"Plan '{input_dto.plan_id}' not found or not active.")

        # Cancel existing subscriptions
        self._sub_repo.cancel_active_by_user(input_dto.user_id)

        # Create new subscription
        new_subscription = Subscription.create(
            user_id=input_dto.user_id,
            plan_id=input_dto.plan_id,
            status=SubscriptionStatus.ACTIVE,
        )
        saved = self._sub_repo.save(new_subscription)
        return _subscription_to_dto(saved)

