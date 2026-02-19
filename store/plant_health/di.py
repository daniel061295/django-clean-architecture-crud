from injector import Module, provider, singleton
from store.plant_health.domain.interfaces import PlantHealthService
from store.plant_health.infrastructure.ai.services import GeminiPlantHealthService
from store.plant_health.application.use_cases import AnalyzePlantHealth
import os

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
        api_key = os.environ.get("GEMINI_API_KEY")
        return GeminiPlantHealthService(api_key=api_key)

    @provider
    def provide_analyze_plant_health(self, service: PlantHealthService) -> AnalyzePlantHealth:
        return AnalyzePlantHealth(service)
