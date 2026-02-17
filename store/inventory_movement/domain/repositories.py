from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from store.inventory_movement.domain.entities import InventoryMovement

class InventoryMovementRepository(ABC):
    """
    Interface for InventoryMovement repository.
    """

    @abstractmethod
    def save(self, movement: InventoryMovement) -> InventoryMovement:
        pass

    @abstractmethod
    def get_by_id(self, movement_id: UUID) -> Optional[InventoryMovement]:
        pass
    
    @abstractmethod
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[InventoryMovement], int]:
        pass
