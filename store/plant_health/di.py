from injector import Module, provider, singleton

from billing.domain.interfaces import DailyUsageRepository, PlanRepository, SubscriptionRepository
from identity.domain.interfaces import UserRepository
from store.plant_health.domain.interfaces import PlantHealthService
from store.plant_health.infrastructure.ai.services import GeminiPlantHealthService
from store.plant_health.application.use_cases import AnalyzePlantHealth
from store.history.application.use_cases import CreateHistoryUseCase
from django.conf import settings


class PlantHealthModule(Module):
    """
    Dependency Injection Module for Plant Health features.

    Wires PlantHealthService and all SaaS guardrail repositories
    (UserRepository, SubscriptionRepository, PlanRepository, DailyUsageRepository)
    into the AnalyzePlantHealth use case.
    """

    @provider
    @singleton
    def provide_plant_health_service(self) -> PlantHealthService:
        """Provides the PlantHealthService implementation."""
        api_key = getattr(settings, "GEMINI_API_KEY", "")
        return GeminiPlantHealthService(api_key=api_key)

    @provider
    def provide_analyze_plant_health(
        self,
        service: PlantHealthService,
        create_history_use_case: CreateHistoryUseCase,
        user_repository: UserRepository,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
        daily_usage_repository: DailyUsageRepository,
    ) -> AnalyzePlantHealth:
        """Provides a fully assembled AnalyzePlantHealth use case."""
        return AnalyzePlantHealth(
            service=service,
            create_history_use_case=create_history_use_case,
            user_repository=user_repository,
            subscription_repository=subscription_repository,
            plan_repository=plan_repository,
            daily_usage_repository=daily_usage_repository,
        )
