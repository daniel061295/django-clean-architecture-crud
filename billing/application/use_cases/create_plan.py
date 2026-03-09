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

class CreatePlan:
    """Creates a new SaaS plan (admin-only operation)."""

    @inject
    def __init__(self, plan_repository: PlanRepository) -> None:
        self._plan_repo = plan_repository

    def execute(self, input_dto: CreatePlanInputDTO) -> PlanOutputDTO:
        """
        Creates a new plan.

        Args:
            input_dto: Plan creation data.

        Returns:
            PlanOutputDTO: The newly created plan.

        Raises:
            PlanAlreadyExistsError: If a plan with the same name already exists.
        """
        existing = [p for p in self._plan_repo.list_all() if p.name == input_dto.name]
        if existing:
            raise PlanAlreadyExistsError(f"Plan '{input_dto.name}' already exists.")

        plan = Plan.create(
            name=input_dto.name,
            price=input_dto.price,
            scan_limit_per_day=input_dto.scan_limit_per_day,
            ads_enabled=input_dto.ads_enabled,
            features=input_dto.features,
        )
        saved = self._plan_repo.save(plan)
        return _plan_to_dto(saved)


# ---------------------------------------------------------------------------
# Subscription Use Cases
# ---------------------------------------------------------------------------
