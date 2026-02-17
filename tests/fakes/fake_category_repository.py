from typing import List, Optional, Tuple
from uuid import UUID
from store.category.domain.entities import Category
from store.category.domain.repositories import CategoryRepository

class FakeCategoryRepository(CategoryRepository):
    """
    In-memory implementation of CategoryRepository for testing.
    """

    def __init__(self):
        self.categories = {}

    def save(self, category: Category) -> Category:
        self.categories[category.id] = category
        return category

    def get_by_id(self, category_id: UUID) -> Optional[Category]:
        return self.categories.get(category_id)
    
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Category], int]:
        all_categories = list(self.categories.values())
        
        if filters.get("active") is not None:
            all_categories = [c for c in all_categories if c.active == filters["active"]]
            
        start = (page - 1) * page_size
        end = start + page_size
        return all_categories[start:end], len(all_categories)

    def delete(self, category_id: UUID) -> None:
        if category_id in self.categories:
            del self.categories[category_id]
            
    def exists_by_name(self, name: str) -> bool:
        return any(c.name == name for c in self.categories.values())
