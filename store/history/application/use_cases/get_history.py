from store.history.domain.interfaces import HistoryRepository
from store.history.application.dtos import GetHistoryInputDTO, HistoryOutputDTO
from injector import inject
from core.domain.services import StorageServiceInterface

class GetHistoryUseCase:
    """
    Use case for retrieving a history record by ID.
    """

    @inject
    def __init__(self, repository: HistoryRepository, storage_service: StorageServiceInterface):
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: GetHistoryInputDTO) -> HistoryOutputDTO:
        history = self._repository.get_by_id(input_dto.id)
        if not history:
            raise ValueError(f"History with ID {input_dto.id} not found.")
            
        photo_url = history.photo
        if photo_url and not photo_url.startswith("data:image"):
            photo_url = self._storage_service.get_signed_url(history.photo) or history.photo

        return HistoryOutputDTO(
            id=str(history.id),
            is_healthy=history.is_healthy,
            title=history.title,
            diagnosis=history.diagnosis,
            confidence=history.confidence,
            treatment=history.treatment,
            urgency_level=history.urgency_level,
            photo=photo_url,
            user_id=history.user_id,
            created_at=str(history.created_at)
        )
