from typing import List, Optional, Tuple, Dict, Type
from uuid import UUID
from django.db import models
from store.plant_item.domain.entities import PlantItem
from store.plant_item.domain.repositories import PlantItemRepository
from store.plant_item.infrastructure.models import PlantItemModel
from store.plant_item.infrastructure.mappers import PlantItemMapper
from core.infrastructure.django.repositories import DjangoBaseRepository

class DjangoPlantItemRepository(DjangoBaseRepository[PlantItem, PlantItemModel], PlantItemRepository):
    """
    Django implementation of the PlantItemRepository interface.
    Uses the Django ORM to persist data.
    """

    @property
    def model_class(self) -> Type[PlantItemModel]:
        return PlantItemModel

    def _to_db_defaults(self, entity: PlantItem) -> dict:
        return {
            "name": entity.name,
            "description": entity.description,
            "price": entity.price,
            "stock": entity.stock,
            "is_available": entity.is_available,
            "created_at": entity.created_at,
        }

    def _to_domain_entity(self, model_instance: PlantItemModel) -> PlantItem:
        return PlantItemMapper.to_domain(model_instance)

    def _apply_filters(self, queryset: models.QuerySet, filters: dict) -> models.QuerySet:
        if filters.get("min_price") is not None:
            queryset = queryset.filter(price__gte=filters["min_price"])
        if filters.get("max_price") is not None:
            queryset = queryset.filter(price__lte=filters["max_price"])
        if filters.get("is_available") is not None:
            queryset = queryset.filter(is_available=filters["is_available"])
        if filters.get("name_contains") is not None:
            queryset = queryset.filter(name__icontains=filters["name_contains"])
        return queryset

    def exists(self, item_id: UUID) -> bool:
        """Checks existence efficiently."""
        return self.model_class.objects.filter(id=item_id).exists()
