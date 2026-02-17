from typing import List, Optional, Tuple
from uuid import UUID
from store.inventory_movement.domain.entities import InventoryMovement
from store.inventory_movement.domain.repositories import InventoryMovementRepository

class FakeInventoryMovementRepository(InventoryMovementRepository):
    """
    In-memory implementation of InventoryMovementRepository for testing.
    """

    def __init__(self):
        self.movements = {}

    def save(self, movement: InventoryMovement) -> InventoryMovement:
        self.movements[movement.id] = movement
        return movement

    def get_by_id(self, movement_id: UUID) -> Optional[InventoryMovement]:
        return self.movements.get(movement_id)
    
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[InventoryMovement], int]:
        all_movements = list(self.movements.values())
        
        # Filtering
        if filters.get("plant_item_id"):
             all_movements = [m for m in all_movements if m.plant_item_id == filters["plant_item_id"]]

        if filters.get("movement_type"):
             all_movements = [m for m in all_movements if m.movement_type.value == filters["movement_type"]]
            
        start = (page - 1) * page_size
        end = start + page_size
        return all_movements[start:end], len(all_movements)
