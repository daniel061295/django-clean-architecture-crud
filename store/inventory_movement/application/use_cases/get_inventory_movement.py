from uuid import UUID
from typing import Optional
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.application.dtos import InventoryMovementResponseDTO

class GetInventoryMovement:
    """
    Use case for retrieving a single Inventory Movement.
    """

    def __init__(self, repository: InventoryMovementRepository):
        self.repository = repository

    def execute(self, movement_id: UUID) -> Optional[InventoryMovementResponseDTO]:
        """
        Executes the use case for retrieving a single Inventory Movement.

        Args:
            movement_id: UUID of the inventory movement.

        Returns:
            InventoryMovementResponseDTO with the retrieved data.
        """
        movement = self.repository.get_by_id(movement_id)
        if not movement:
            return None
            
        return InventoryMovementResponseDTO(
            id=movement.id,
            plant_item_id=movement.plant_item_id,
            movement_type=movement.movement_type.value,
            quantity=movement.quantity,
            reason=movement.reason,
            timestamp=movement.timestamp,
            created_at=movement.created_at
        )
