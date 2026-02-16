from uuid import UUID
from store.domain.repositories import PlantItemRepository
from store.domain.exceptions import PlantItemNotFoundError
from store.application.dtos import UpdatePlantItemDTO, PlantItemResponseDTO

class UpdatePlantItem:
    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, item_id: UUID, dto: UpdatePlantItemDTO) -> PlantItemResponseDTO:
        item = self.repository.get_by_id(item_id)
        if not item:
            raise PlantItemNotFoundError(f"PlantItem with id {item_id} not found")
        
        item.update(
            name=dto.name,
            description=dto.description,
            price=dto.price,
            stock=dto.stock
        )
        
        updated_item = self.repository.save(item)
        
        return PlantItemResponseDTO(
            id=updated_item.id,
            name=updated_item.name,
            description=updated_item.description,
            price=updated_item.price,
            stock=updated_item.stock,
            is_available=updated_item.is_available,
            created_at=updated_item.created_at
        )
