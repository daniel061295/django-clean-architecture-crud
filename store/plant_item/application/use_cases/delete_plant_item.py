from uuid import UUID
from store.plant_item.domain.repositories import PlantItemRepository
from store.plant_item.domain.exceptions import PlantItemNotFoundError


class DeletePlantItem:
    """
    Use case for deleting a PlantItem.
    """

    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, item_id: UUID) -> None:
        """
        Executes the deletion logic.

        Args:
            item_id (UUID): The ID of the item to delete.

        Raises:
            PlantItemNotFoundError: If the item does not exist.
        """
        if not self.repository.exists(item_id):
            raise PlantItemNotFoundError(f"PlantItem with id {item_id} not found")

        self.repository.delete(item_id)
