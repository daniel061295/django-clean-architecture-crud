from store.domain.entities import PlantItem
from store.domain.repositories import PlantItemRepository
from store.application.dtos import CreatePlantItemDTO, PlantItemResponseDTO


class CreatePlantItem:
    """
    Use case for creating a new PlantItem.
    """

    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, dto: CreatePlantItemDTO) -> PlantItemResponseDTO:
        """
        Executes the creation logic.

        Args:
            dto (CreatePlantItemDTO): Data for the new item.

        Returns:
            PlantItemResponseDTO: The created item.
        """
        plant_item = PlantItem.create(
            name=dto.name, description=dto.description, price=dto.price, stock=dto.stock
        )
        saved_item = self.repository.save(plant_item)

        return PlantItemResponseDTO(
            id=saved_item.id,
            name=saved_item.name,
            description=saved_item.description,
            price=saved_item.price,
            stock=saved_item.stock,
            is_available=saved_item.is_available,
            created_at=saved_item.created_at,
        )
