from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from store.category.domain.entities import Category

class CategoryRepository(ABC):
    """
    Interface for Category repository.
    """

    @abstractmethod
    def save(self, category: Category) -> Category:
        """Saves or updates a Category."""
        pass

    @abstractmethod
    def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """Retrieves a Category by ID."""
        pass
    
    @abstractmethod
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Category], int]:
        """Lists categories with pagination and filtering."""
        pass

    @abstractmethod
    def delete(self, category_id: UUID) -> None:
        """Deletes a Category by ID."""
        pass
        
    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """Checks if a category with the given name exists."""
        pass
