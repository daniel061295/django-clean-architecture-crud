from typing import List, Optional, Tuple
from uuid import UUID
from django.core.paginator import Paginator
from store.inventory_movement.domain.entities import InventoryMovement
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.infrastructure.models import InventoryMovementModel
from store.inventory_movement.infrastructure.mappers import InventoryMovementMapper

class DjangoInventoryMovementRepository(InventoryMovementRepository):
    """
    Django implementation of the InventoryMovementRepository interface.
    """

    def save(self, movement: InventoryMovement) -> InventoryMovement:
        """
        Saves an InventoryMovement.

        Args:
            movement: InventoryMovement to save.

        Returns:
            InventoryMovement with the saved data.
        """
        model = InventoryMovementMapper.to_db(movement)
        model.save()
        return InventoryMovementMapper.to_domain(model)

    def get_by_id(self, movement_id: UUID) -> Optional[InventoryMovement]:
        """
        Retrieves an InventoryMovement by its ID.

        Args:
            movement_id: UUID of the inventory movement.

        Returns:
            InventoryMovement with the retrieved data.
        """
        try:
            model = InventoryMovementModel.objects.get(id=movement_id)
            return InventoryMovementMapper.to_domain(model)
        except InventoryMovementModel.DoesNotExist:
            return None

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[InventoryMovement], int]:
        """
        Retrieves a list of InventoryMovements.

        Args:
            page: Page number.
            page_size: Number of items per page.
            filters: Dictionary of filters.

        Returns:
            Tuple of InventoryMovements and total count.
        """ 
        queryset = InventoryMovementModel.objects.all().order_by("-timestamp")

        if filters.get("plant_item_id"):
             queryset = queryset.filter(plant_item_id=filters["plant_item_id"])
        
        if filters.get("movement_type"):
            queryset = queryset.filter(movement_type=filters["movement_type"])

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return [InventoryMovementMapper.to_domain(item) for item in page_obj], paginator.count
