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

class AuthorizePlantScan:
    """
    Authorizes a plant scan operation by checking all required conditions.
    
    This is a composite use case that orchestrates multiple checks:
    1. User has an active subscription
    2. User has not exceeded their daily scan limit
    
    This use case encapsulates the business rules for plant scanning authorization.
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

    def execute(self, user_id: UUID) -> AuthorizePlantScanOutputDTO:
        """
        Authorizes a plant scan for a user.

        Args:
            user_id: UUID of the user requesting the scan.

        Returns:
            AuthorizePlantScanOutputDTO: Authorization result with details.
        """
        # Check active subscription
        subscription = self._sub_repo.get_active_by_user(user_id)
        
        if subscription is None or subscription.status != SubscriptionStatus.ACTIVE:
            return AuthorizePlantScanOutputDTO(
                authorized=False,
                reason="no_active_subscription",
            )

        # Get plan details
        plan = self._plan_repo.get_by_id(subscription.plan_id)
        
        if plan is None:
            return AuthorizePlantScanOutputDTO(
                authorized=False,
                reason="plan_not_found",
            )

        # Check daily scan limit
        usage = self._usage_repo.get_today_usage(user_id)
        scans_today = usage.scans_count if usage else 0
        scan_limit = plan.scan_limit_per_day

        # If no limit is set, authorize
        if scan_limit is None:
            return AuthorizePlantScanOutputDTO(
                authorized=True,
                plan_name=plan.name,
                scans_today=scans_today,
                scan_limit=None,
            )

        # Check if limit exceeded
        if scans_today >= scan_limit:
            return AuthorizePlantScanOutputDTO(
                authorized=False,
                reason="scan_limit_exceeded",
                plan_name=plan.name,
                scans_today=scans_today,
                scan_limit=scan_limit,
            )

        # All checks passed
        return AuthorizePlantScanOutputDTO(
            authorized=True,
            plan_name=plan.name,
            scans_today=scans_today,
            scan_limit=scan_limit,
        )


# ---------------------------------------------------------------------------
# Create Subscription Use Cases
# ---------------------------------------------------------------------------
