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

class CheckDailyScanLimit:
    """
    Checks if a user has exceeded their daily scan limit.
    
    This use case verifies the user's scan usage against their plan's limits.
    """

    @inject
    def __init__(
        self,
        daily_usage_repository: DailyUsageRepository,
        plan_repository: PlanRepository,
    ) -> None:
        self._usage_repo = daily_usage_repository
        self._plan_repo = plan_repository

    def execute(self, input_dto: CheckDailyScanLimitInputDTO) -> CheckDailyScanLimitOutputDTO:
        """
        Checks if a user can perform another scan today.

        Args:
            input_dto: User UUID and plan ID.

        Returns:
            CheckDailyScanLimitOutputDTO: Whether the user can scan and usage info.
        """
        usage = self._usage_repo.get_today_usage(input_dto.user_id)
        scans_today = usage.scans_count if usage else 0

        plan = self._plan_repo.get_by_id(input_dto.plan_id)
        scan_limit = plan.scan_limit_per_day if plan else None

        # If no limit is set, user can scan
        if scan_limit is None:
            return CheckDailyScanLimitOutputDTO(
                can_scan=True,
                scans_today=scans_today,
                scan_limit=None,
            )

        return CheckDailyScanLimitOutputDTO(
            can_scan=scans_today < scan_limit,
            scans_today=scans_today,
            scan_limit=scan_limit,
        )

