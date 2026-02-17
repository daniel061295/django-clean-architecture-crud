from typing import List, Optional, Tuple
from uuid import UUID
from store.plant_item.domain.entities import PlantItem
from store.plant_item.domain.repositories import PlantItemRepository

class FakePlantItemRepository(PlantItemRepository):
    """
    In-memory implementation of PlantItemRepository for testing.
    """

    def __init__(self):
        self.items = {}

    def save(self, plant_item: PlantItem) -> PlantItem:
        self.items[plant_item.id] = plant_item
        return plant_item

    def get_by_id(self, item_id: UUID) -> Optional[PlantItem]:
        return self.items.get(item_id)

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[PlantItem], int]:
        all_items = list(self.items.values())
        
        # Filtering
        if filters.get("min_price") is not None:
            all_items = [i for i in all_items if i.price >= filters["min_price"]]
            
        if filters.get("max_price") is not None:
             all_items = [i for i in all_items if i.price <= filters["max_price"]]
             
        if filters.get("is_available") is not None:
            all_items = [i for i in all_items if i.is_available == filters["is_available"]]
            
        if filters.get("name_contains"):
            all_items = [i for i in all_items if filters["name_contains"].lower() in i.name.lower()]

        start = (page - 1) * page_size
        end = start + page_size
        return all_items[start:end], len(all_items)

    def delete(self, item_id: UUID) -> None:
        if item_id in self.items:
            del self.items[item_id]

    def exists(self, item_id: UUID) -> bool:
        return item_id in self.items
