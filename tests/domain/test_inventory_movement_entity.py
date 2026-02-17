import pytest
from uuid import uuid4, UUID
from datetime import datetime
from store.inventory_movement.domain.entities import InventoryMovement, MovementType

def test_create_inventory_movement_success():
    """Test successful creation of an inventory movement."""
    plant_item_id = uuid4()
    quantity = 10
    reason = "Stock refill"
    
    movement = InventoryMovement.create(
        plant_item_id=plant_item_id,
        movement_type=MovementType.ENTRADA,
        quantity=quantity,
        reason=reason
    )
    
    assert isinstance(movement.id, UUID)
    assert movement.plant_item_id == plant_item_id
    assert movement.movement_type == MovementType.ENTRADA
    assert movement.quantity == quantity
    assert movement.reason == reason
    assert isinstance(movement.timestamp, datetime)
    assert isinstance(movement.created_at, datetime)

def test_create_inventory_movement_negative_quantity_fails():
    """Test that creating a movement with negative quantity fails."""
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        InventoryMovement.create(uuid4(), MovementType.ENTRADA, -5)

def test_create_inventory_movement_zero_quantity_fails():
    """Test that creating a movement with zero quantity fails."""
    with pytest.raises(ValueError, match="Quantity must be greater than 0"):
        InventoryMovement.create(uuid4(), MovementType.ENTRADA, 0)
