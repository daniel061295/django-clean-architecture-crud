import pytest
from unittest.mock import patch
from uuid import uuid4
from store.plant_item.domain.entities import PlantItem
from store.inventory_movement.domain.entities import MovementType
from store.inventory_movement.application.use_cases.register_inventory_movement import RegisterInventoryMovement
from store.inventory_movement.application.use_cases.get_inventory_movement import GetInventoryMovement
from store.inventory_movement.application.use_cases.list_inventory_movements import ListInventoryMovements
from store.inventory_movement.application.dtos import RegisterInventoryMovementDTO
from tests.fakes.fake_inventory_movement_repository import FakeInventoryMovementRepository
from tests.fakes.fake_plant_item_repository import FakePlantItemRepository
from store.plant_item.domain.exceptions import InvalidStockError

@patch('django.db.transaction.atomic')
def test_register_entrada_movement(mock_atomic):
    move_repo = FakeInventoryMovementRepository()
    plant_repo = FakePlantItemRepository()
    
    plant = PlantItem.create("Rose", "Desc", 10.0, 5)
    plant_repo.save(plant)
    
    use_case = RegisterInventoryMovement(move_repo, plant_repo)
    dto = RegisterInventoryMovementDTO(
        plant_item_id=plant.id,
        movement_type="ENTRADA",
        quantity=5,
        reason="Restock"
    )
    
    result = use_case.execute(dto)
    
    # Check movement saved
    assert result.movement_type == "ENTRADA"
    assert result.quantity == 5
    assert move_repo.get_by_id(result.id) is not None
    
    # Check plant stock updated
    updated_plant = plant_repo.get_by_id(plant.id)
    assert updated_plant.stock == 10 # 5 + 5

@patch('django.db.transaction.atomic')
def test_register_salida_movement_success(mock_atomic):
    move_repo = FakeInventoryMovementRepository()
    plant_repo = FakePlantItemRepository()
    
    plant = PlantItem.create("Rose", "Desc", 10.0, 10)
    plant_repo.save(plant)
    
    use_case = RegisterInventoryMovement(move_repo, plant_repo)
    dto = RegisterInventoryMovementDTO(
        plant_item_id=plant.id,
        movement_type="SALIDA",
        quantity=3,
        reason="Sold"
    )
    
    use_case.execute(dto)
    
    updated_plant = plant_repo.get_by_id(plant.id)
    assert updated_plant.stock == 7 # 10 - 3

@patch('django.db.transaction.atomic')
def test_register_salida_insufficient_stock(mock_atomic):
    move_repo = FakeInventoryMovementRepository()
    plant_repo = FakePlantItemRepository()
    
    plant = PlantItem.create("Rose", "Desc", 10.0, 2)
    plant_repo.save(plant)
    
    use_case = RegisterInventoryMovement(move_repo, plant_repo)
    dto = RegisterInventoryMovementDTO(
        plant_item_id=plant.id,
        movement_type="SALIDA",
        quantity=5,
        reason="Oversip"
    )
    
    with pytest.raises(InvalidStockError, match="Insufficient stock"):
        use_case.execute(dto)

@patch('django.db.transaction.atomic')
def test_register_ajuste_movement(mock_atomic):
    move_repo = FakeInventoryMovementRepository()
    plant_repo = FakePlantItemRepository()
    
    plant = PlantItem.create("Rose", "Desc", 10.0, 5)
    plant_repo.save(plant)
    
    use_case = RegisterInventoryMovement(move_repo, plant_repo)
    dto = RegisterInventoryMovementDTO(
        plant_item_id=plant.id,
        movement_type="AJUSTE",
        quantity=2,
        reason="Found extra"
    )
    
    use_case.execute(dto)
    
    updated_plant = plant_repo.get_by_id(plant.id)
    assert updated_plant.stock == 2 # Set to specific value (User changed logic to absolute set)

def test_get_inventory_movement_use_case():
    # Setup
    move_repo = FakeInventoryMovementRepository()
    plant_repo = FakePlantItemRepository() # Not used by GET but good for completeness/usecase if needed
    
    # Needs valid movement in repo (easiest via register or manual insert but let's register)
    # Actually register is complex, manual insert easier for Unit Test of GET
    # But entity creation is complex? No, entity.create is fine.
    
    from store.inventory_movement.domain.entities import InventoryMovement
    
    movement = InventoryMovement.create(uuid4(), MovementType.ENTRADA, 5)
    move_repo.save(movement)
    
    use_case = GetInventoryMovement(move_repo)
    result = use_case.execute(movement.id)
    
    assert result.id == movement.id
    assert result.quantity == 5

def test_list_inventory_movements_use_case():
    move_repo = FakeInventoryMovementRepository()
    
    from store.inventory_movement.domain.entities import InventoryMovement
    plant_id = uuid4()
    
    move_repo.save(InventoryMovement.create(plant_id, MovementType.ENTRADA, 5))
    move_repo.save(InventoryMovement.create(plant_id, MovementType.SALIDA, 2))
    move_repo.save(InventoryMovement.create(uuid4(), MovementType.ENTRADA, 10))
    
    use_case = ListInventoryMovements(move_repo)
    results, count = use_case.execute(page=1, page_size=10, filters={"plant_item_id": plant_id})
    
    assert count >= 2
    assert len(results) == 2
    assert all(r.plant_item_id == plant_id for r in results)
