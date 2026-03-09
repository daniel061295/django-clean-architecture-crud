from typing import List
from store.history.domain.interfaces import HistoryRepository
from store.history.application.dtos import GetHistoryByUserInputDTO, HistoryOutputDTO
from injector import inject
from core.domain.services import StorageServiceInterface

class GetHistoryByUserUseCase:
    """
    Use case for retrieving all history records for a specific user.
    """

    @inject
    def __init__(self, repository: HistoryRepository, storage_service: StorageServiceInterface):
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: GetHistoryByUserInputDTO) -> List[HistoryOutputDTO]:
        histories = self._repository.get_by_user_id(input_dto.user_id)
        dtos = []
        for h in histories:
            photo_url = h.photo
            if photo_url and not photo_url.startswith("data:image"):
                photo_url = self._storage_service.get_signed_url(h.photo) or h.photo
            dtos.append(HistoryOutputDTO(
                id=str(h.id),
                is_healthy=h.is_healthy,
                title=h.title,
                diagnosis=h.diagnosis,
                confidence=h.confidence,
                treatment=h.treatment,
                urgency_level=h.urgency_level,
                photo=photo_url,
                user_id=h.user_id,
                created_at=str(h.created_at)
            ))
        return dtos
