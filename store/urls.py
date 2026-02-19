from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store.plant_item.interfaces.views import PlantItemView
from store.category.interfaces.views import CategoryView
from store.provider.interfaces.views import ProviderView
from store.inventory_movement.interfaces.views import InventoryMovementView
from store.sale.interfaces.views import SaleView
from store.plant_health.interfaces.views import PlantHealthView

router = DefaultRouter()
router.register(r"plant-items", PlantItemView, basename="plant-items")
router.register(r"categories", CategoryView, basename="categories")
router.register(r"providers", ProviderView, basename="providers")
router.register(r"inventory-movements", InventoryMovementView, basename="inventory-movements")
router.register(r"sales", SaleView, basename="sales")
router.register(r"plant-health", PlantHealthView, basename="plant-health")

urlpatterns = [
    path("", include(router.urls)),
]
