"""
Billing Application Use Cases — Business orchestration for SaaS billing.

Each class handles a single, specific business action following the Command Pattern.
"""
from datetime import date
from typing import List
from uuid import UUID

from injector import inject

from billing.application.dtos import (
    ChangePlanInputDTO,
    CancelSubscriptionInputDTO,
    CreatePlanInputDTO,
    MySubscriptionOutputDTO,
    PlanOutputDTO,
    SubscriptionOutputDTO,
)
from billing.domain.entities import Plan, Subscription
from billing.domain.exceptions import (
    NoActiveSubscriptionError,
    PlanAlreadyExistsError,
    PlanNotFoundError,
)
from billing.domain.interfaces import DailyUsageRepository, PlanRepository, SubscriptionRepository
from billing.domain.value_objects import SubscriptionStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan_to_dto(plan: Plan) -> PlanOutputDTO:
    return PlanOutputDTO(
        id=str(plan.id),
        name=plan.name,
        price=plan.price,
        scan_limit_per_day=plan.scan_limit_per_day,
        ads_enabled=plan.ads_enabled,
        features=plan.features,
        is_active=plan.is_active,
    )


def _subscription_to_dto(sub: Subscription) -> SubscriptionOutputDTO:
    return SubscriptionOutputDTO(
        id=str(sub.id),
        user_id=str(sub.user_id),
        plan_id=str(sub.plan_id),
        status=sub.status.value,
        start_date=sub.start_date.isoformat(),
        end_date=sub.end_date.isoformat() if sub.end_date else None,
        external_id=sub.external_id,
    )


# ---------------------------------------------------------------------------
# Plan Use Cases
# ---------------------------------------------------------------------------

class GetAvailablePlans:
    """Returns all publicly available (active) plans."""

    @inject
    def __init__(self, plan_repository: PlanRepository) -> None:
        self._plan_repo = plan_repository

    def execute(self) -> List[PlanOutputDTO]:
        """Returns a list of all active plans."""
        return [_plan_to_dto(p) for p in self._plan_repo.list_active()]


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
