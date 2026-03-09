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

class CancelSubscription:
    """Cancels the user's active subscription immediately."""

    @inject
    def __init__(self, subscription_repository: SubscriptionRepository) -> None:
        self._sub_repo = subscription_repository

    def execute(self, input_dto: CancelSubscriptionInputDTO) -> None:
        """
        Cancels the user's active subscription.

        Args:
            input_dto: User UUID.

        Raises:
            NoActiveSubscriptionError: If the user has no active subscription to cancel.
        """
        subscription = self._sub_repo.get_active_by_user(input_dto.user_id)
        if subscription is None:
            raise NoActiveSubscriptionError("No active subscription found to cancel.")

        self._sub_repo.cancel_active_by_user(input_dto.user_id)


# ---------------------------------------------------------------------------
# Authorization Use Cases
# ---------------------------------------------------------------------------
