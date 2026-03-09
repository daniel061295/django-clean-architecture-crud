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

class CreateSubscription:
    """
    Creates a subscription for a user.
    
    This use case verifies that:
    1. The plan exists
    2. The user doesn't have an active subscription already
    3. Creates and persists the subscription
    """
    
    @inject
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
    ):
        self._subscription_repo = subscription_repo
        self._plan_repo = plan_repo
    
    def execute(self, input_dto: CreateSubscriptionInputDTO) -> SubscriptionOutputDTO:
        """
        Creates a subscription for a user.
        
        Args:
            input_dto: Input data containing user_id, plan_id, and dates.
            
        Returns:
            SubscriptionOutputDTO: The created subscription.
            
        Raises:
            PlanNotFoundError: If the specified plan doesn't exist.
            SubscriptionAlreadyExistsError: If user already has active subscription.
        """
        # 1. Verify plan exists
        plan = self._plan_repo.get_by_id(input_dto.plan_id)
        if plan is None:
            raise PlanNotFoundError(f"Plan with id '{input_dto.plan_id}' not found.")
        
        # 2. Check user doesn't have active subscription
        existing = self._subscription_repo.get_active_by_user(input_dto.user_id)
        if existing is not None:
            raise SubscriptionAlreadyExistsError(
                f"User '{input_dto.user_id}' already has an active subscription."
            )
        
        # 3. Create subscription using entity factory
        subscription = Subscription.create(
            user_id=input_dto.user_id,
            plan_id=input_dto.plan_id,
            end_date=input_dto.end_date,
        )
        
        # 4. Persist
        saved = self._subscription_repo.save(subscription)
        return _subscription_to_dto(saved)

