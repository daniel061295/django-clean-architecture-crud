from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from store.plant_item.domain.entities import PlantItem


class PlantItemRepository(ABC):
    """
    Interface for PlantItem repository.
    Defines abstract methods for data persistence operations.
    """

    @abstractmethod
    def save(self, plant_item: PlantItem) -> PlantItem:
        """
        Saves or updates a PlantItem.

        Args:
            plant_item (PlantItem): The entity to save.

        Returns:
            PlantItem: The saved entity.
        """

    @abstractmethod
    def get_by_id(self, item_id: UUID) -> Optional[PlantItem]:
        """
        Retrieves a PlantItem by its ID.

        Args:
            item_id (UUID): The ID to search for.

        Returns:
            Optional[PlantItem]: The found entity or None.
        """

    @abstractmethod
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[PlantItem], int]:
        """
        Lists PlantItems with pagination and filtering.

        Args:
            page (int): Page number (1-based).
            page_size (int): Items per page.
            filters (dict): Filter criteria.

        Returns:
            Tuple[List[PlantItem], int]: A tuple containing the list of items and the total count.
        """

    @abstractmethod
    def delete(self, item_id: UUID) -> None:
        """
        Deletes a PlantItem by its ID.

        Args:
            item_id (UUID): The ID to delete.
        """

    @abstractmethod
    def exists(self, item_id: UUID) -> bool:
        """
        Checks if a PlantItem exists.

        Args:
            item_id (UUID): The ID to check.

        Returns:
            bool: True if exists, else False.
        """
