"""
Billing Dependency Injection Module.

Binds all billing domain interfaces to their Django ORM implementations.
"""
from injector import Binder, Module

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
