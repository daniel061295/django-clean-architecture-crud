from injector import Module, Binder
from store.category.di import CategoryModule
from store.plant_item.di import PlantItemModule
from store.provider.di import ProviderModule
from store.inventory_movement.di import InventoryMovementModule
from store.sale.di import SaleModule

class StoreModule(Module):
    """
    Dependency Injection Module for the Store application.
    Aggregates entity-specific modules.
    """

    def configure(self, binder: Binder):
        binder.install(CategoryModule())
        binder.install(PlantItemModule())
        binder.install(ProviderModule())
        binder.install(InventoryMovementModule())
        binder.install(SaleModule())
