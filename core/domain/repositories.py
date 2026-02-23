from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, Tuple, TypeVar

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """
    Generic Base Repository Interface (Clean Architecture - Domain Layer).
    
    This interface defines the standard CRUD operations that any concrete
    repository must implement, independent of the underlying database engine.
    """

    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Saves or updates an entity.
        
        Args:
            entity: The domain entity to save.
            
        Returns:
            The saved domain entity.
        """
        pass

    @abstractmethod
    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Retrieves an entity by its unique identifier.
        
        Args:
            entity_id: The unique identifier of the entity.
            
        Returns:
            The domain entity if found, or None.
        """
        pass

    @abstractmethod
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[T], int]:
        """
        Lists entities with pagination and optional filtering.
        
        Args:
            page: The page number (1-indexed).
            page_size: The number of items per page.
            filters: A dictionary of filter criteria.
            
        Returns:
            A tuple containing a list of domain entities and the total count.
        """
        pass

    @abstractmethod
    def delete(self, entity_id: Any) -> None:
        """
        Deletes an entity by its unique identifier.
        
        Args:
            entity_id: The unique identifier of the entity to delete.
            
        Returns:
            None
        """
        pass
