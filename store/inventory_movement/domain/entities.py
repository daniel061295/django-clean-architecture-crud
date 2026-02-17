from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum
from typing import Optional

class MovementType(Enum):
    """
    Enum representing the type of inventory movement.
    """ 
    ENTRADA = "ENTRADA"
    SALIDA = "SALIDA"
    AJUSTE = "AJUSTE"

@dataclass
class InventoryMovement:
    """
    Domain entity representing an inventory movement.
    """
    id: UUID
    plant_item_id: UUID
    movement_type: MovementType
    quantity: int
    reason: Optional[str]
    timestamp: datetime
    created_at: datetime

    @classmethod
    def create(cls, plant_item_id: UUID, movement_type: MovementType, quantity: int, reason: str = None) -> "InventoryMovement":
        """
        Creates a new InventoryMovement.

        Args:
            plant_item_id: UUID of the plant item.
            movement_type: Type of inventory movement.
            quantity: Quantity of the inventory movement.
            reason: Reason for the inventory movement.

        Returns:
            InventoryMovement with the created data.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0.")
        
        now = datetime.now(timezone.utc)
        return cls(
            id=uuid4(),
            plant_item_id=plant_item_id,
            movement_type=movement_type,
            quantity=quantity,
            reason=reason,
            timestamp=now,
            created_at=now,
        )
