from typing import List, Tuple
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.application.dtos import InventoryMovementResponseDTO

class ListInventoryMovements:
    """
    Use case for listing Inventory Movements.
    """

    def __init__(self, repository: InventoryMovementRepository):
        self.repository = repository

    def execute(self, page: int, page_size: int, filters: dict) -> Tuple[List[InventoryMovementResponseDTO], int]:
        movements, total_count = self.repository.list(page, page_size, filters)
        
        dtos = [
            InventoryMovementResponseDTO(
                id=m.id,
                plant_item_id=m.plant_item_id,
                movement_type=m.movement_type.value,
                quantity=m.quantity,
                reason=m.reason,
                timestamp=m.timestamp,
                created_at=m.created_at
            )
            for m in movements
        ]
        
        return dtos, total_count
