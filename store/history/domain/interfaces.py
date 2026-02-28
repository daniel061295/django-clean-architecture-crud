from abc import ABC, abstractmethod
from typing import Optional, List
from store.history.domain.entities import History

class HistoryRepository(ABC):
    """
    Interface for History Data Access.
    """

    @abstractmethod
    def save(self, history: History) -> History:
        """
        Saves a history record.
        """
        pass

    @abstractmethod
    def get_by_id(self, history_id: str) -> Optional[History]:
        """
        Retrieves a history record by its ID.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[History]:
        """
        Retrieves all history records.
        """
        pass

    @abstractmethod
    def get_by_user_id(self, user_id: str) -> List[History]:
        """
        Retrieves all history records for a specific user.
        """
        pass

    @abstractmethod
    def delete(self, history_id: str) -> bool:
        """
        Deletes a history record by its ID.
        Returns True if successful, False if the record was not found.
        """
        pass

    @abstractmethod
    def delete_all(self) -> None:
        """
        Deletes all history records.
        """
        pass
