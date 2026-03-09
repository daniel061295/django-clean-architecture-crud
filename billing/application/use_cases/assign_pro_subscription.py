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

class AssignProSubscription:
    """
    Assigns a PRO subscription to a user, canceling any existing FREE subscription.
    
    This use case:
    1. Cancels any active FREE subscription
    2. Creates a new PRO subscription with 30-day duration
    
    PRO subscription has a 30-day duration and will expire.
    """
    
    PRO_PLAN_DEFAULT_DURATION_DAYS = 30

    @inject
    def __init__(
        self,
        subscription_repo: SubscriptionRepository,
        plan_repo: PlanRepository,
    ):
        self._subscription_repo = subscription_repo
        self._plan_repo = plan_repo

    def execute(self, user_id: UUID) -> SubscriptionOutputDTO:
        """
        Assigns a PRO subscription to a user.
        Cancels any existing FREE subscription and creates new PRO with 30-day duration.

        Args:
            user_id: UUID of the user.

        Returns:
            SubscriptionOutputDTO: The created PRO subscription.

        Raises:
            PlanNotFoundError: If the PRO plan doesn't exist.
        """
        # 1. Get PRO plan
        pro_plan = self._get_pro_plan()

        # 2. Cancel any existing active subscriptions (FREE or otherwise)
        self._subscription_repo.cancel_active_by_user(user_id)

        # 3. Calculate end date (30 days from now)
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=self.PRO_PLAN_DEFAULT_DURATION_DAYS)

        # 4. Create PRO subscription
        subscription = Subscription.create(
            user_id=user_id,
            plan_id=pro_plan.id,
            end_date=end_date,
        )

        # 5. Persist
        saved = self._subscription_repo.save(subscription)
        return _subscription_to_dto(saved)

    def _get_pro_plan(self) -> Plan:
        """Helper to get PRO plan by name."""
        from billing.infrastructure.models import PlanModel
        from billing.infrastructure.mappers import PlanMapper

        try:
            model = PlanModel.objects.get(name="PRO")
            return PlanMapper.to_domain(model)
        except PlanModel.DoesNotExist:
            raise PlanNotFoundError("PRO plan not found. Please seed the database first.")
