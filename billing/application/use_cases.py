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


# ---------------------------------------------------------------------------
# Authorization Use Cases
# ---------------------------------------------------------------------------

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
