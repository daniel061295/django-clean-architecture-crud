from injector import Module, provider, singleton
from store.plant_health.domain.interfaces import PlantHealthService
from store.plant_health.infrastructure.ai.services import GeminiPlantHealthService
from store.plant_health.application.use_cases import AnalyzePlantHealth
from store.history.application.use_cases import CreateHistoryUseCase
from django.conf import settings


class PlantHealthModule(Module):
    """
    Dependency Injection Module for Plant Health features.
    """

    @provider
    @singleton
    def provide_plant_health_service(self) -> PlantHealthService:
        """
        Provides the PlantHealthService implementation.
        """
        api_key = getattr(settings, "GEMINI_API_KEY", "")
        return GeminiPlantHealthService(api_key=api_key)

    @provider
    def provide_analyze_plant_health(self, service: PlantHealthService, create_history_use_case: CreateHistoryUseCase) -> AnalyzePlantHealth:
        return AnalyzePlantHealth(service, create_history_use_case)

