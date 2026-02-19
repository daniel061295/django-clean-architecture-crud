from store.plant_health.domain.interfaces import PlantHealthService
from store.plant_health.application.dtos import AnalyzePlantHealthInputDTO, PlantHealthAnalysisResponseDTO
from injector import inject

class AnalyzePlantHealth:
    """
    Use Case for analyzing plant health from a photo.
    """

    @inject
    def __init__(self, service: PlantHealthService):
        self._service = service

    def execute(self, input_dto: AnalyzePlantHealthInputDTO) -> PlantHealthAnalysisResponseDTO:
        """
        Executes the plant health analysis.

        Args:
            input_dto: Input DTO containing the photo.

        Returns:
            PlantHealthAnalysisResponseDTO: The analysis result.
        """
        report = self._service.analyze_photo(input_dto.photo)
        
        return PlantHealthAnalysisResponseDTO(
            is_healthy=report.is_healthy,
            diagnosis=report.diagnosis,
            confidence=report.confidence,
            treatment=report.treatment,
            urgency_level=report.urgency_level
        )
