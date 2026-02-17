from uuid import UUID
from store.plant_item.domain.repositories import PlantItemRepository
from store.plant_item.domain.exceptions import PlantItemNotFoundError
from store.plant_item.application.dtos import UpdatePlantItemDTO, PlantItemResponseDTO


class UpdatePlantItem:
    """
    Use case for updating an existing PlantItem.
    """

    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, item_id: UUID, dto: UpdatePlantItemDTO) -> PlantItemResponseDTO:
        """
        Executes the update logic.

        Args:
            item_id (UUID): The ID of the item to update.
            dto (UpdatePlantItemDTO): The update data.

        Returns:
            PlantItemResponseDTO: The updated item.

        Raises:
            PlantItemNotFoundError: If the item does not exist.
            DomainError: If validation fails.
        """
        item = self.repository.get_by_id(item_id)
        if not item:
            raise PlantItemNotFoundError(f"PlantItem with id {item_id} not found")

        item.update(name=dto.name, description=dto.description, price=dto.price, stock=dto.stock)

        updated_item = self.repository.save(item)

        return PlantItemResponseDTO(
            id=updated_item.id,
            name=updated_item.name,
            description=updated_item.description,
            price=updated_item.price,
            stock=updated_item.stock,
            is_available=updated_item.is_available,
            created_at=updated_item.created_at,
        )
