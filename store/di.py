from injector import Module, provider, singleton
from store.plant_item.domain.repositories import PlantItemRepository
from store.plant_item.infrastructure.repositories import DjangoPlantItemRepository
from store.plant_item.application.use_cases.create_plant_item import CreatePlantItem
from store.plant_item.application.use_cases.list_plant_items import ListPlantItems
from store.plant_item.application.use_cases.get_plant_item import GetPlantItem
from store.plant_item.application.use_cases.update_plant_item import UpdatePlantItem
from store.plant_item.application.use_cases.delete_plant_item import DeletePlantItem
from store.category.domain.repositories import CategoryRepository
from store.category.infrastructure.repositories import DjangoCategoryRepository
from store.category.application.use_cases.create_category import CreateCategory
from store.category.application.use_cases.list_categories import ListCategories
from store.category.application.use_cases.get_category import GetCategory
from store.category.application.use_cases.update_category import UpdateCategory
from store.category.application.use_cases.delete_category import DeleteCategory
from store.provider.domain.repositories import ProviderRepository
from store.provider.infrastructure.repositories import DjangoProviderRepository
from store.provider.application.use_cases.create_provider import CreateProvider
from store.provider.application.use_cases.list_providers import ListProviders
from store.provider.application.use_cases.get_provider import GetProvider
from store.provider.application.use_cases.update_provider import UpdateProvider
from store.provider.application.use_cases.delete_provider import DeleteProvider
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.infrastructure.repositories import DjangoInventoryMovementRepository
from store.inventory_movement.application.use_cases.register_inventory_movement import RegisterInventoryMovement
from store.inventory_movement.application.use_cases.list_inventory_movements import ListInventoryMovements
from store.inventory_movement.application.use_cases.get_inventory_movement import GetInventoryMovement
from store.sale.domain.repositories import SaleRepository
from store.sale.infrastructure.repositories import DjangoSaleRepository
from store.sale.application.use_cases.create_sale import CreateSale
from store.sale.application.use_cases.add_sale_detail import AddSaleDetail
from store.sale.application.use_cases.complete_sale import CompleteSale
from store.sale.application.use_cases.list_sales import ListSales
from store.sale.application.use_cases.get_sale import GetSale


class StoreModule(Module):
    """
    Dependency Injection Module for the Store application.
    Binds interfaces to implementations and provides use cases.
    """

    @provider
    @singleton
    def provide_repository(self) -> PlantItemRepository:
        """
        Provides the PlantItemRepository implementation.
        """
        return DjangoPlantItemRepository()

    @provider
    def provide_create_plant_item(self, repository: PlantItemRepository) -> CreatePlantItem:
        """
        Provides the CreatePlantItem use case.
        """
        return CreatePlantItem(repository)

    @provider
    def provide_list_plant_items(self, repository: PlantItemRepository) -> ListPlantItems:
        """
        Provides the ListPlantItems use case.
        """
        return ListPlantItems(repository)

    @provider
    def provide_get_plant_item(self, repository: PlantItemRepository) -> GetPlantItem:
        """
        Provides the GetPlantItem use case.
        """
        return GetPlantItem(repository)

    @provider
    def provide_update_plant_item(self, repository: PlantItemRepository) -> UpdatePlantItem:
        """
        Provides the UpdatePlantItem use case.
        """
        return UpdatePlantItem(repository)

    @provider
    def provide_delete_plant_item(self, repository: PlantItemRepository) -> DeletePlantItem:
        """
        Provides the DeletePlantItem use case.
        """
        return DeletePlantItem(repository)

    @provider
    @singleton
    def provide_category_repository(self) -> CategoryRepository:
        """
        Provides the CategoryRepository implementation.
        """
        return DjangoCategoryRepository()

    @provider
    def provide_create_category(self, repository: CategoryRepository) -> CreateCategory:
        """
        Provides the CreateCategory use case.
        """
        return CreateCategory(repository)

    @provider
    def provide_list_categories(self, repository: CategoryRepository) -> ListCategories:
        """
        Provides the ListCategories use case.
        """
        return ListCategories(repository)

    @provider
    def provide_get_category(self, repository: CategoryRepository) -> GetCategory:
        """
        Provides the GetCategory use case.
        """
        return GetCategory(repository)
    
    @provider
    def provide_update_category(self, repository: CategoryRepository) -> UpdateCategory:
        """
        Provides the UpdateCategory use case.
        """
        return UpdateCategory(repository)
    
    @provider
    def provide_delete_category(self, repository: CategoryRepository) -> DeleteCategory:
        """
        Provides the DeleteCategory use case.
        """
        return DeleteCategory(repository)

    @provider
    @singleton
    def provide_provider_repository(self) -> ProviderRepository:
        """
        Provides the ProviderRepository implementation.
        """
        return DjangoProviderRepository()

    @provider
    def provide_create_provider(self, repository: ProviderRepository) -> CreateProvider:
        """
        Provides the CreateProvider use case.
        """
        return CreateProvider(repository)

    @provider
    def provide_list_providers(self, repository: ProviderRepository) -> ListProviders:
        """
        Provides the ListProviders use case.
        """
        return ListProviders(repository)

    @provider
    def provide_get_provider(self, repository: ProviderRepository) -> GetProvider:
        """
        Provides the GetProvider use case.
        """
        return GetProvider(repository)

    @provider
    def provide_update_provider(self, repository: ProviderRepository) -> UpdateProvider:
        """
        Provides the UpdateProvider use case.
        """
        return UpdateProvider(repository)

    @provider
    def provide_delete_provider(self, repository: ProviderRepository) -> DeleteProvider:
        """
        Provides the DeleteProvider use case.
        """
        return DeleteProvider(repository)

    @provider
    @singleton
    def provide_inventory_movement_repository(self) -> InventoryMovementRepository:
        """
        Provides the InventoryMovementRepository implementation.
        """
        return DjangoInventoryMovementRepository()

    @provider
    def provide_register_inventory_movement(self, repository: InventoryMovementRepository, plant_item_repo: PlantItemRepository) -> RegisterInventoryMovement:
        """
        Provides the RegisterInventoryMovement use case.
        """
        return RegisterInventoryMovement(repository, plant_item_repo)

    @provider
    def provide_list_inventory_movements(self, repository: InventoryMovementRepository) -> ListInventoryMovements:
        """
        Provides the ListInventoryMovements use case.
        """
        return ListInventoryMovements(repository)

    @provider
    def provide_get_inventory_movement(self, repository: InventoryMovementRepository) -> GetInventoryMovement:
        """
        Provides the GetInventoryMovement use case.
        """
        return GetInventoryMovement(repository)

    @provider
    @singleton
    def provide_sale_repository(self) -> SaleRepository:
        """
        Provides the SaleRepository implementation.
        """
        return DjangoSaleRepository()

    @provider
    def provide_create_sale(self, repository: SaleRepository) -> CreateSale:
        """
        Provides the CreateSale use case.
        """
        return CreateSale(repository)

    @provider
    def provide_add_sale_detail(self, repository: SaleRepository) -> AddSaleDetail:
        """
        Provides the AddSaleDetail use case.
        """
        return AddSaleDetail(repository)

    @provider
    def provide_complete_sale(self, repository: SaleRepository, inventory_use_case: RegisterInventoryMovement) -> CompleteSale:
        """
        Provides the CompleteSale use case.
        """
        return CompleteSale(repository, inventory_use_case)

    @provider
    def provide_list_sales(self, repository: SaleRepository) -> ListSales:
        """
        Provides the ListSales use case.
        """
        return ListSales(repository)

    @provider
    def provide_get_sale(self, repository: SaleRepository) -> GetSale:
        """
        Provides the GetSale use case.
        """
        return GetSale(repository)
