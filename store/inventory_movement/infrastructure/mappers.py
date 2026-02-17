from store.inventory_movement.domain.entities import InventoryMovement, MovementType
from store.inventory_movement.infrastructure.models import InventoryMovementModel

class InventoryMovementMapper:
    """
    Mapper between InventoryMovement domain entity and InventoryMovementModel Django model.
    """

    @staticmethod
    def to_domain(model: InventoryMovementModel) -> InventoryMovement:
        return InventoryMovement(
            id=model.id,
            plant_item_id=model.plant_item_id,
            movement_type=MovementType(model.movement_type),
            quantity=model.quantity,
            reason=model.reason,
            timestamp=model.timestamp,
            created_at=model.created_at
        )

    @staticmethod
    def to_db(entity: InventoryMovement) -> InventoryMovementModel:
        return InventoryMovementModel(
            id=entity.id,
            plant_item_id=entity.plant_item_id,
            movement_type=entity.movement_type.value,
            quantity=entity.quantity,
            reason=entity.reason,
            timestamp=entity.timestamp,
            created_at=entity.created_at
        )
