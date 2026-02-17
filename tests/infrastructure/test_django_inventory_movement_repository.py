import pytest
from uuid import uuid4
from store.inventory_movement.domain.entities import InventoryMovement, MovementType
from store.inventory_movement.infrastructure.repositories import DjangoInventoryMovementRepository

@pytest.mark.django_db
def test_inventory_movement_repository_crud():
    repo = DjangoInventoryMovementRepository()
    plant_id = uuid4()
    
    # Create
    movement = InventoryMovement.create(plant_id, MovementType.ENTRADA, 10, "Initial Stock")
    saved = repo.save(movement)
    
    assert saved.id == movement.id
    assert saved.plant_item_id == plant_id
    assert saved.movement_type == MovementType.ENTRADA
    
    # Get by ID
    retrieved = repo.get_by_id(movement.id)
    assert retrieved is not None
    assert retrieved.id == movement.id
    assert retrieved.quantity == 10

@pytest.mark.django_db
def test_inventory_movement_repository_list_filters():
    repo = DjangoInventoryMovementRepository()
    plant_id_1 = uuid4()
    plant_id_2 = uuid4()
    
    m1 = InventoryMovement.create(plant_id_1, MovementType.ENTRADA, 5)
    m2 = InventoryMovement.create(plant_id_1, MovementType.SALIDA, 2)
    m3 = InventoryMovement.create(plant_id_2, MovementType.ENTRADA, 10)
    
    repo.save(m1)
    repo.save(m2)
    repo.save(m3)
    
    # List all
    results, count = repo.list(1, 10, {})
    assert count >= 3
    
    # Filter by plant_item_id
    results, count = repo.list(1, 10, {"plant_item_id": plant_id_1})
    assert len(results) == 2
    assert all(r.plant_item_id == plant_id_1 for r in results)
    
    # Filter by movement_type
    results, count = repo.list(1, 10, {"movement_type": MovementType.SALIDA.value})
    # Might catch other test data if not careful, but usually isolated db per test run or transaction rollback
    # We check if m2 is in results
    found = any(r.id == m2.id for r in results)
    assert found
