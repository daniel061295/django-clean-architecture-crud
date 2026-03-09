from store.tips.domain.interfaces import TipRepository
from store.tips.application.dtos import TipOutputDTO
from injector import inject

class GetRandomTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self) -> TipOutputDTO:
        tip = self._repository.get_random()
        if not tip:
            raise ValueError("No tips available.")
            
        return TipOutputDTO(
            id=str(tip.id),
            title=tip.title,
            description=tip.description,
            icon=tip.icon,
            created_at=str(tip.created_at)
        )
