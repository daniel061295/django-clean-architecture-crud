from injector import Module, provider, singleton
from store.domain.repositories import PlantItemRepository
from store.infrastructure.repositories import DjangoPlantItemRepository
from store.application.use_cases.create_plant_item import CreatePlantItem
from store.application.use_cases.list_plant_items import ListPlantItems
from store.application.use_cases.get_plant_item import GetPlantItem
from store.application.use_cases.update_plant_item import UpdatePlantItem
from store.application.use_cases.delete_plant_item import DeletePlantItem


class StoreModule(Module):
    """
    Dependency Injection Module for the Store application.
    Binds interfaces to implementations and provides use cases.
    """

    @provider
    @singleton
    def provide_repository(self) -> PlantItemRepository:
        return DjangoPlantItemRepository()

    @provider
    def provide_create_plant_item(self, repository: PlantItemRepository) -> CreatePlantItem:
        return CreatePlantItem(repository)

    @provider
    def provide_list_plant_items(self, repository: PlantItemRepository) -> ListPlantItems:
        return ListPlantItems(repository)

    @provider
    def provide_get_plant_item(self, repository: PlantItemRepository) -> GetPlantItem:
        return GetPlantItem(repository)

    @provider
    def provide_update_plant_item(self, repository: PlantItemRepository) -> UpdatePlantItem:
        return UpdatePlantItem(repository)

    @provider
    def provide_delete_plant_item(self, repository: PlantItemRepository) -> DeletePlantItem:
        return DeletePlantItem(repository)
