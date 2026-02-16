from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from store.domain.entities import PlantItem

class PlantItemRepository(ABC):
    @abstractmethod
    def save(self, plant_item: PlantItem) -> PlantItem:
        pass

    @abstractmethod
    def get_by_id(self, item_id: UUID) -> Optional[PlantItem]:
        pass

    @abstractmethod
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[PlantItem], int]:
        """Returns a tuple of (items, total_count)"""
        pass

    @abstractmethod
    def delete(self, item_id: UUID) -> None:
        pass

    @abstractmethod
    def exists(self, item_id: UUID) -> bool:
        pass
