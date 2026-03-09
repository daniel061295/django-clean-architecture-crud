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

class CreateFreeSubscriptionForNewUser:
    """
    Creates a FREE subscription automatically for newly registered users.

    This use case is designed to be called silently after user registration.
    If the user already has a subscription, it returns successfully without error.
    
    FREE subscription is PERMANENT (no end date).
    """

    @inject
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
    ):
        self._subscription_repo = subscription_repo
        self._plan_repo = plan_repo

    def execute(self, input_dto: CreateFreeSubscriptionForUserInputDTO) -> SubscriptionOutputDTO:
        """
        Creates a FREE subscription for a newly registered user.
        FREE subscription has no end date (permanent).

        Args:
            input_dto: Input data containing user_id.

        Returns:
            SubscriptionOutputDTO: The created or existing subscription.

        Raises:
            PlanNotFoundError: If the FREE plan doesn't exist.
        """
        # 1. Check if user already has active subscription (silent success)
        existing = self._subscription_repo.get_active_by_user(input_dto.user_id)
        if existing is not None:
            return _subscription_to_dto(existing)

        # 2. Get FREE plan
        free_plan = self._get_free_plan()

        # 3. Create subscription with NO end date (permanent)
        subscription = Subscription.create(
            user_id=input_dto.user_id,
            plan_id=free_plan.id,
            end_date=None,  # FREE is permanent
        )

        # 4. Persist
        saved = self._subscription_repo.save(subscription)
        return _subscription_to_dto(saved)

    def _get_free_plan(self) -> Plan:
        """Helper to get FREE plan by name."""
        # Search for FREE plan by name
        from billing.infrastructure.models import PlanModel
        from billing.infrastructure.mappers import PlanMapper

        try:
            model = PlanModel.objects.get(name="FREE")
            return PlanMapper.to_domain(model)
        except PlanModel.DoesNotExist:
            raise PlanNotFoundError("FREE plan not found. Please seed the database first.")

