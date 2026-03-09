from store.history.domain.interfaces import HistoryRepository
from store.history.application.dtos import GetHistoryInputDTO
from injector import inject
from core.domain.services import StorageServiceInterface

class DeleteHistoryUseCase:
    """
    Use case for deleting a history record by ID.
    """

    @inject
    def __init__(self, repository: HistoryRepository, storage_service: StorageServiceInterface):
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: GetHistoryInputDTO) -> None:
        history = self._repository.get_by_id(input_dto.id)
        if not history:
            raise ValueError(f"History with ID {input_dto.id} not found.")
            
        if history.photo and not history.photo.startswith("data:image"):
            try:
                self._storage_service.delete_file(history.photo)
            except Exception:
                pass

        success = self._repository.delete(input_dto.id)
        if not success:
            raise ValueError(f"History with ID {input_dto.id} not found.")
