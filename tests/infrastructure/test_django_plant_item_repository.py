import pytest
from uuid import uuid4
from store.plant_item.domain.entities import PlantItem
from store.plant_item.infrastructure.repositories import DjangoPlantItemRepository

@pytest.mark.django_db
def test_plant_item_repository_crud():
    repo = DjangoPlantItemRepository()
    
    # Create
    item = PlantItem.create("Rose", "Red", 10.0, 5)
    saved = repo.save(item)
    assert saved.id == item.id
    assert saved.name == "Rose"
    
    # Get by ID
    retrieved = repo.get_by_id(item.id)
    assert retrieved is not None
    assert retrieved.id == item.id
    assert retrieved.price == 10.0
    
    # Exists
    assert repo.exists(item.id) is True
    assert repo.exists(uuid4()) is False
    
    # Update
    item.update(name="Blue Rose", price=20.0)
    repo.save(item)
    updated = repo.get_by_id(item.id)
    assert updated.name == "Blue Rose"
    assert updated.price == 20.0
    
    # Delete
    repo.delete(item.id)
    assert repo.get_by_id(item.id) is None

@pytest.mark.django_db
def test_plant_item_repository_list_filters():
    repo = DjangoPlantItemRepository()
    
    p1 = PlantItem.create("Rose", "Red", 10.0, 5)
    p2 = PlantItem.create("Lily", "White", 20.0, 0) # price 20, stock 0 -> unavailable
    p3 = PlantItem.create("Tulip", "Yellow", 30.0, 10)
    
    repo.save(p1)
    repo.save(p2)
    repo.save(p3)
    
    # List all
    results, count = repo.list(1, 10, {})
    assert count >= 3
    
    # Filter by min price
    results, count = repo.list(1, 10, {"min_price": 15.0})
    assert len(results) >= 2 # Lily and Tulip
    
    # Filter by max price
    results, count = repo.list(1, 10, {"max_price": 15.0})
    assert len(results) == 1 # Rose (assuming clean db or at least one match)
    assert results[0].name == "Rose"
    
    # Filter by availablity
    results, count = repo.list(1, 10, {"is_available": False})
    # Should get Lily (stock 0)
    # Note: Depending on existing DB state, might act differently. But tests usually run in transaction rollback.
    match = next((i for i in results if i.name == "Lily"), None)
    assert match is not None
    
    # Filter by name contains
    results, count = repo.list(1, 10, {"name_contains": "lip"})
    assert len(results) == 1 # Tulip
    assert results[0].name == "Tulip"
