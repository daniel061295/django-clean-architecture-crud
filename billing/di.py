"""
Billing Dependency Injection Module.

Binds all billing domain interfaces to their Django ORM implementations.
"""
from injector import Binder, Module, provider

from billing.application.use_cases import (
    AuthorizePlantScan,
    CancelSubscription,
    ChangePlan,
    CheckDailyScanLimit,
    CheckSubscriptionStatus,
    CreateFreeSubscriptionForNewUser,
    CreatePlan,
    CreateSubscription,
    GetAvailablePlans,
    GetMySubscription,
)
from billing.domain.interfaces import DailyUsageRepository, PlanRepository, SubscriptionRepository
from billing.infrastructure.repositories import (
    DjangoDailyUsageRepository,
    DjangoPlanRepository,
    DjangoSubscriptionRepository,
)


class BillingModule(Module):
    """
    Dependency injection bindings for the Billing bounded context.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(PlanRepository, to=DjangoPlanRepository)
        binder.bind(SubscriptionRepository, to=DjangoSubscriptionRepository)
        binder.bind(DailyUsageRepository, to=DjangoDailyUsageRepository)

    @provider
    def provide_get_available_plans(self, plan_repository: PlanRepository) -> GetAvailablePlans:
        """Provides GetAvailablePlans use case."""
        return GetAvailablePlans(plan_repository)

    @provider
    def provide_create_plan(self, plan_repository: PlanRepository) -> CreatePlan:
        """Provides CreatePlan use case."""
        return CreatePlan(plan_repository)

    @provider
    def provide_get_my_subscription(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
        daily_usage_repository: DailyUsageRepository,
    ) -> GetMySubscription:
        """Provides GetMySubscription use case."""
        return GetMySubscription(subscription_repository, plan_repository, daily_usage_repository)

    @provider
    def provide_change_plan(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
    ) -> ChangePlan:
        """Provides ChangePlan use case."""
        return ChangePlan(subscription_repository, plan_repository)

    @provider
    def provide_cancel_subscription(
        self, subscription_repository: SubscriptionRepository
    ) -> CancelSubscription:
        """Provides CancelSubscription use case."""
        return CancelSubscription(subscription_repository)

    # Authorization Use Cases
    @provider
    def provide_check_subscription_status(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
    ) -> CheckSubscriptionStatus:
        """Provides CheckSubscriptionStatus use case."""
        return CheckSubscriptionStatus(subscription_repository, plan_repository)

    @provider
    def provide_check_daily_scan_limit(
        self,
        daily_usage_repository: DailyUsageRepository,
        plan_repository: PlanRepository,
    ) -> CheckDailyScanLimit:
        """Provides CheckDailyScanLimit use case."""
        return CheckDailyScanLimit(daily_usage_repository, plan_repository)

    @provider
    def provide_authorize_plant_scan(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
        daily_usage_repository: DailyUsageRepository,
    ) -> AuthorizePlantScan:
        """Provides AuthorizePlantScan use case."""
        return AuthorizePlantScan(subscription_repository, plan_repository, daily_usage_repository)

    # Create Subscription Use Cases
    @provider
    def provide_create_subscription(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
    ) -> CreateSubscription:
        """Provides CreateSubscription use case."""
        return CreateSubscription(subscription_repository, plan_repository)

    @provider
    def provide_create_free_subscription_for_new_user(
        self,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
    ) -> CreateFreeSubscriptionForNewUser:
        """Provides CreateFreeSubscriptionForNewUser use case."""
        return CreateFreeSubscriptionForNewUser(subscription_repository, plan_repository)
