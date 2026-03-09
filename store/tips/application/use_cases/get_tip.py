import uuid
from store.tips.domain.interfaces import TipRepository
from store.tips.application.dtos import TipOutputDTO
from injector import inject

class GetTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self, tip_id: uuid.UUID) -> TipOutputDTO:
        tip = self._repository.get_by_id(tip_id)
        if not tip:
            raise ValueError(f"Tip with ID {tip_id} not found.")
            
        return TipOutputDTO(
            id=str(tip.id),
            title=tip.title,
            description=tip.description,
            icon=tip.icon,
            created_at=str(tip.created_at)
        )
