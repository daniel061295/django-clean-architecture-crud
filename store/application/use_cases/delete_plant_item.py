from uuid import UUID
from store.domain.repositories import PlantItemRepository
from store.domain.exceptions import PlantItemNotFoundError

class DeletePlantItem:
    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, item_id: UUID) -> None:
        if not self.repository.exists(item_id):
            raise PlantItemNotFoundError(f"PlantItem with id {item_id} not found")
        
        self.repository.delete(item_id)
