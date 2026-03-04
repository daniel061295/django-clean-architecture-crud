from store.history.domain.entities import History
from store.history.domain.interfaces import HistoryRepository
from store.history.application.dtos import CreateHistoryInputDTO, HistoryOutputDTO, GetHistoryInputDTO, GetHistoryByUserInputDTO
from typing import List
from injector import inject
from core.domain.services import StorageServiceInterface

class CreateHistoryUseCase:
    """
    Use case for creating a new AI plant health diagnosis history record.
    """
    
    @inject
    def __init__(self, repository: HistoryRepository):
        self._repository = repository

    def execute(self, input_dto: CreateHistoryInputDTO) -> HistoryOutputDTO:
        # 1. Create Domain Entity
        history = History(
            is_healthy=input_dto.is_healthy,
            title=input_dto.title,
            diagnosis=input_dto.diagnosis,
            confidence=input_dto.confidence,
            treatment=input_dto.treatment,
            urgency_level=input_dto.urgency_level,
            photo=input_dto.photo,
            user_id=input_dto.user_id
        )
        
        # 2. Persist
        saved_history = self._repository.save(history)
        
        # 3. Return Output DTO
        return HistoryOutputDTO(
            id=str(saved_history.id),
            is_healthy=saved_history.is_healthy,
            title=saved_history.title,
            diagnosis=saved_history.diagnosis,
            confidence=saved_history.confidence,
            treatment=saved_history.treatment,
            urgency_level=saved_history.urgency_level,
            photo=saved_history.photo,
            user_id=saved_history.user_id,
            created_at=str(saved_history.created_at)
        )

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

class GetAllHistoryUseCase:
    """
    Use case for retrieving all history records.
    """

    @inject
    def __init__(self, repository: HistoryRepository, storage_service: StorageServiceInterface):
        self._repository = repository
        self._storage_service = storage_service

    def execute(self) -> List[HistoryOutputDTO]:
        histories = self._repository.get_all()
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

class DeleteHistoryUseCase:
    """
    Use case for deleting a history record by ID.
    """

    @inject
    def __init__(self, repository: HistoryRepository):
        self._repository = repository

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

class DeleteAllHistoryUseCase:
    """
    Use case for deleting all history records.
    """

    @inject
    def __init__(self, repository: HistoryRepository):
        self._repository = repository

    def execute(self) -> None:
        self._repository.delete_all()
