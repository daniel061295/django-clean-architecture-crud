from typing import List, Optional, Tuple, Type
from uuid import UUID
from django.db import models
from store.inventory_movement.domain.entities import InventoryMovement
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.infrastructure.models import InventoryMovementModel
from store.inventory_movement.infrastructure.mappers import InventoryMovementMapper
from core.infrastructure.django.repositories import DjangoBaseRepository

class DjangoInventoryMovementRepository(DjangoBaseRepository[InventoryMovement, InventoryMovementModel], InventoryMovementRepository):
    """
    Django implementation of the InventoryMovementRepository interface.
    """

    @property
    def model_class(self) -> Type[InventoryMovementModel]:
        return InventoryMovementModel

    def _to_db_defaults(self, entity: InventoryMovement) -> dict:
        return {
            "plant_item_id": entity.plant_item_id,
            "quantity": entity.quantity,
            "movement_type": entity.movement_type.value,
            "reason": entity.reason,
            "timestamp": entity.timestamp
        }

    def _to_domain_entity(self, model_instance: InventoryMovementModel) -> InventoryMovement:
        return InventoryMovementMapper.to_domain(model_instance)

    def _apply_filters(self, queryset: models.QuerySet, filters: dict) -> models.QuerySet:
        queryset = queryset.order_by("-timestamp")
        if filters.get("plant_item_id"):
             queryset = queryset.filter(plant_item_id=filters["plant_item_id"])
        if filters.get("movement_type"):
            queryset = queryset.filter(movement_type=filters["movement_type"])
        return queryset
