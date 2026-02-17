import pytest
from uuid import uuid4
from store.plant_item.domain.entities import PlantItem
from store.plant_item.application.use_cases.create_plant_item import CreatePlantItem
from store.plant_item.application.use_cases.get_plant_item import GetPlantItem
from store.plant_item.application.use_cases.list_plant_items import ListPlantItems
from store.plant_item.application.use_cases.update_plant_item import UpdatePlantItem
from store.plant_item.application.use_cases.delete_plant_item import DeletePlantItem
from store.plant_item.application.dtos import (
    CreatePlantItemDTO, 
    UpdatePlantItemDTO, 
    ListPlantItemsQueryDTO
)
from store.plant_item.domain.exceptions import PlantItemNotFoundError
from tests.fakes.fake_plant_item_repository import FakePlantItemRepository

def test_create_plant_item_use_case():
    repo = FakePlantItemRepository()
    use_case = CreatePlantItem(repo)
    
    dto = CreatePlantItemDTO(name="Rose", description="Red", price=10.0, stock=5)
    result = use_case.execute(dto)
    
    assert result.name == "Rose"
    assert result.price == 10.0
    assert repo.exists(result.id)

def test_get_plant_item_use_case_found():
    repo = FakePlantItemRepository()
    plant = PlantItem.create("Lily", "White", 8.0, 10)
    repo.save(plant)
    
    use_case = GetPlantItem(repo)
    result = use_case.execute(plant.id)
    
    assert result.id == plant.id
    assert result.name == "Lily"

def test_get_plant_item_use_case_not_found():
    repo = FakePlantItemRepository()
    use_case = GetPlantItem(repo)
    
    with pytest.raises(PlantItemNotFoundError):
        use_case.execute(uuid4())

def test_list_plant_items_use_case():
    repo = FakePlantItemRepository()
    repo.save(PlantItem.create("Rose", "Red", 10.0, 5))
    repo.save(PlantItem.create("Lily", "White", 8.0, 10))
    repo.save(PlantItem.create("Tulip", "Yellow", 5.0, 20))
    
    use_case = ListPlantItems(repo)
    query = ListPlantItemsQueryDTO(page=1, page_size=10)
    result = use_case.execute(query)
    
    assert result.total_count == 3
    assert len(result.items) == 3

def test_list_plant_items_use_case_filter():
    repo = FakePlantItemRepository()
    repo.save(PlantItem.create("Rose", "Red", 10.0, 5)) # Available
    repo.save(PlantItem.create("Withered", "Dead", 8.0, 0)) # Not available
    
    use_case = ListPlantItems(repo)
    query = ListPlantItemsQueryDTO(is_available=True)
    result = use_case.execute(query)
    
    assert result.total_count == 1
    assert result.items[0].name == "Rose"

def test_update_plant_item_use_case_success():
    repo = FakePlantItemRepository()
    plant = PlantItem.create("Old", "Desc", 10.0, 5)
    repo.save(plant)
    
    use_case = UpdatePlantItem(repo)
    dto = UpdatePlantItemDTO(name="New", price=15.0)
    
    result = use_case.execute(plant.id, dto)
    
    assert result.name == "New"
    assert result.price == 15.0
    assert result.stock == 5 # Unchanged

def test_update_plant_item_use_case_not_found():
    repo = FakePlantItemRepository()
    use_case = UpdatePlantItem(repo)
    dto = UpdatePlantItemDTO(name="New")
    
    with pytest.raises(PlantItemNotFoundError):
        use_case.execute(uuid4(), dto)

def test_delete_plant_item_use_case_success():
    repo = FakePlantItemRepository()
    plant = PlantItem.create("To Delete", "Desc", 10.0, 5)
    repo.save(plant)
    
    use_case = DeletePlantItem(repo)
    use_case.execute(plant.id)
    
    assert repo.get_by_id(plant.id) is None

def test_delete_plant_item_use_case_not_found():
    repo = FakePlantItemRepository()
    use_case = DeletePlantItem(repo)
    
    with pytest.raises(PlantItemNotFoundError):
        use_case.execute(uuid4())
