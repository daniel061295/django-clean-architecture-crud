from store.history.domain.interfaces import HistoryRepository
from injector import inject

class DeleteAllHistoryUseCase:
    """
    Use case for deleting all history records.
    """

    @inject
    def __init__(self, repository: HistoryRepository):
        self._repository = repository

    def execute(self) -> None:
        self._repository.delete_all()
