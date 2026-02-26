from store.plant_health.domain.interfaces import PlantHealthService
from store.plant_health.application.dtos import AnalyzePlantHealthInputDTO, PlantHealthAnalysisResponseDTO
from store.history.application.use_cases import CreateHistoryUseCase
from store.history.application.dtos import CreateHistoryInputDTO
from injector import inject
import logging
import base64

class AnalyzePlantHealth:
    """
    Use Case for analyzing plant health from a photo.
    """

    @inject
    def __init__(self, service: PlantHealthService, create_history_use_case: CreateHistoryUseCase):
        self._service = service
        self._create_history_use_case = create_history_use_case

    def execute(self, input_dto: AnalyzePlantHealthInputDTO) -> PlantHealthAnalysisResponseDTO:
        """
        Executes the plant health analysis.

        Args:
            input_dto: Input DTO containing the photo.

        Returns:
            PlantHealthAnalysisResponseDTO: The analysis result.
        """
        report = self._service.analyze_photo(input_dto.photo)
        
        # Save history silently
        try:
            # We need to get the photo as base64 string
            input_dto.photo.seek(0)
            photo_bytes = input_dto.photo.read()
            photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
            
            history_dto = CreateHistoryInputDTO(
                is_healthy=report.is_healthy,
                title=report.title,
                diagnosis=report.diagnosis,
                confidence=report.confidence,
                treatment=report.treatment,
                urgency_level=report.urgency_level,
                photo=photo_base64
            )
            self._create_history_use_case.execute(history_dto)
        except Exception as e:
            logging.error(f"Failed to save plant health history: {str(e)}", exc_info=True)
        
        return PlantHealthAnalysisResponseDTO(
            is_healthy=report.is_healthy,
            title=report.title,
            diagnosis=report.diagnosis,
            confidence=report.confidence,
            treatment=report.treatment,
            urgency_level=report.urgency_level,
            photo=photo_base64
        )
