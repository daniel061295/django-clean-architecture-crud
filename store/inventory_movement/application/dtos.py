from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional
from store.inventory_movement.domain.entities import MovementType

@dataclass
class RegisterInventoryMovementDTO:
    plant_item_id: UUID
    movement_type: str  # String input, will be converted to Enum
    quantity: int
    reason: Optional[str] = None

@dataclass
class InventoryMovementResponseDTO:
    id: UUID
    plant_item_id: UUID
    movement_type: str
    quantity: int
    reason: Optional[str]
    timestamp: datetime
    created_at: datetime
