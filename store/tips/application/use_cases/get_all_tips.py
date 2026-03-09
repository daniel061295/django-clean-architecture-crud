from typing import List
from store.tips.domain.interfaces import TipRepository
from store.tips.application.dtos import TipOutputDTO
from injector import inject

class GetAllTipsUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self) -> List[TipOutputDTO]:
        tips = self._repository.get_all()
        return [
            TipOutputDTO(
                id=str(t.id),
                title=t.title,
                description=t.description,
                icon=t.icon,
                created_at=str(t.created_at)
            ) for t in tips
        ]
