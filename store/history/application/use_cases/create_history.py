from store.history.domain.entities import History
from store.history.domain.interfaces import HistoryRepository
from store.history.application.dtos import CreateHistoryInputDTO, HistoryOutputDTO
from injector import inject

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
