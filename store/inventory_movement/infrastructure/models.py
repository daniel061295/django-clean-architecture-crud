from django.db import models
from core.models import BaseModel
from store.inventory_movement.domain.entities import MovementType

class InventoryMovementModel(BaseModel):
    """
    Django ORM model for InventoryMovement.
    """
    plant_item_id = models.UUIDField(null=False) 
    movement_type = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in MovementType])
    quantity = models.IntegerField()
    reason = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = "inventory_movements"
        verbose_name = "Inventory Movement"
        verbose_name_plural = "Inventory Movements"
        app_label = "store"

    def __str__(self):
        return f"{self.movement_type} - {self.quantity}"
