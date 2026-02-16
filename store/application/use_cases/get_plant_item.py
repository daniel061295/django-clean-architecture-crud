from uuid import UUID
from store.domain.repositories import PlantItemRepository
from store.domain.exceptions import PlantItemNotFoundError
from store.application.dtos import PlantItemResponseDTO


class GetPlantItem:
    """
    Use case for retrieving a single PlantItem by ID.
    """

    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, item_id: UUID) -> PlantItemResponseDTO:
        """
        Executes the retrieval logic.

        Args:
            item_id (UUID): The ID of the item to retrieve.

        Returns:
            PlantItemResponseDTO: The found item.

        Raises:
            PlantItemNotFoundError: If the item does not exist.
        """
        item = self.repository.get_by_id(item_id)
        if not item:
            raise PlantItemNotFoundError(f"PlantItem with id {item_id} not found")

        return PlantItemResponseDTO(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            stock=item.stock,
            is_available=item.is_available,
            created_at=item.created_at,
        )
