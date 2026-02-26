from abc import ABC, abstractmethod
from typing import List, Optional
import uuid

from store.tips.domain.entities import Tip

class TipRepository(ABC):
    """
    Abstract Base Class for Tip persistence.
    """

    @abstractmethod
    def save(self, tip: Tip) -> Tip:
        pass

    @abstractmethod
    def get_by_id(self, tip_id: uuid.UUID) -> Optional[Tip]:
        pass

    @abstractmethod
    def get_all(self) -> List[Tip]:
        pass

    @abstractmethod
    def get_random(self) -> Optional[Tip]:
        pass

    @abstractmethod
    def delete(self, tip_id: uuid.UUID) -> bool:
        pass
