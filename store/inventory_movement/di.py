from injector import Module, provider, singleton
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.infrastructure.repositories import DjangoInventoryMovementRepository
from store.inventory_movement.application.use_cases.register_inventory_movement import RegisterInventoryMovement
from store.inventory_movement.application.use_cases.list_inventory_movements import ListInventoryMovements
from store.inventory_movement.application.use_cases.get_inventory_movement import GetInventoryMovement
from store.plant_item.domain.repositories import PlantItemRepository

class InventoryMovementModule(Module):
    @provider
    @singleton
    def provide_repository(self) -> InventoryMovementRepository:
        return DjangoInventoryMovementRepository()

    @provider
    def provide_register_inventory_movement(self, repository: InventoryMovementRepository, plant_item_repo: PlantItemRepository) -> RegisterInventoryMovement:
        return RegisterInventoryMovement(repository, plant_item_repo)

    @provider
    def provide_list_inventory_movements(self, repository: InventoryMovementRepository) -> ListInventoryMovements:
        return ListInventoryMovements(repository)

    @provider
    def provide_get_inventory_movement(self, repository: InventoryMovementRepository) -> GetInventoryMovement:
        return GetInventoryMovement(repository)
