from django.urls import path, include
from rest_framework.routers import DefaultRouter
from store.interfaces.views import PlantItemView

router = DefaultRouter()
router.register(r"plant-items", PlantItemView, basename="plant-items")

urlpatterns = [
    path("", include(router.urls)),
]
