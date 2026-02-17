from typing import List, Optional, Tuple, Dict
from uuid import UUID
from store.inventory_movement.domain.entities import InventoryMovement
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.infrastructure.models import InventoryMovementModel
from store.inventory_movement.infrastructure.mappers import InventoryMovementMapper
from django.core.paginator import Paginator

class DjangoInventoryMovementRepository(InventoryMovementRepository):
    """
    Django implementation of the InventoryMovementRepository interface.
    """

    def save(self, movement: InventoryMovement) -> InventoryMovement:
        model = InventoryMovementMapper.to_db(movement)
        model.save()
        return InventoryMovementMapper.to_domain(model)

    def get_by_id(self, movement_id: UUID) -> Optional[InventoryMovement]:
        try:
            model = InventoryMovementModel.objects.get(id=movement_id)
            return InventoryMovementMapper.to_domain(model)
        except InventoryMovementModel.DoesNotExist:
            return None

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[InventoryMovement], int]:
        queryset = InventoryMovementModel.objects.all().order_by("-timestamp")

        if filters.get("plant_item_id"):
             queryset = queryset.filter(plant_item_id=filters["plant_item_id"])
        
        if filters.get("movement_type"):
            queryset = queryset.filter(movement_type=filters["movement_type"])

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return [InventoryMovementMapper.to_domain(item) for item in page_obj], paginator.count
