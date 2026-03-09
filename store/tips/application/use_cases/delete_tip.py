import uuid
from store.tips.domain.interfaces import TipRepository
from injector import inject

class DeleteTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self, tip_id: uuid.UUID) -> None:
        success = self._repository.delete(tip_id)
        if not success:
            raise ValueError(f"Tip with ID {tip_id} not found.")
