from django.db import models
import uuid
from store.inventory_movement.domain.entities import MovementType

class InventoryMovementModel(models.Model):
    """
    Django ORM model for InventoryMovement.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Using UUIDField for Foreign Key reference to decouple from PlantItemModel class dependency being strictly imported here if needed, 
    # but normally we use ForeignKey to PlantItemModel. 
    # Since we are in the same 'store' app context for Django, we can use 'store.PlantItemModel' or import it.
    # To keep strict separation, we can just use UUID if we don't need database-level cascade constraints enforced by Django ORM strictly between modules,
    # BUT for a real app, ForeignKey is better.
    # Given Screaming Architecture often creates modules that might be microservices later, UUID is safer.
    # However, for a Monolith with "Screaming Architecture", ForeignKey is usually acceptable if models are in the same DB.
    # The requirement says "Screaming Architecture (organización por dominio)".
    # I will use a ForeignKey to 'store.PlantItemModel' using string reference to avoid circular imports or strict module coupling.
    # Actually, I'll refer to it via the exposed model in models.py or just string.
    # Let's use `plant_item_id` as UUIDField to be strictly decoupled as per "No permitir lógica de negocio en views, serializers ni modelos ORM" implies loose coupling?
    # No, typically Infrastructure layer *implements* the persistence.
    # I'll use UUIDField to avoid importing PlantItemModel and keep modules independent at code level, unless referential integrity is a strict requirement asked.
    # The prompt doesn't explicitly ask for Foreign Keys, but "Las dependencias deben apuntar siempre hacia el dominio".
    # Using UUID avoids importing infrastructure of another module.
    
    plant_item_id = models.UUIDField(null=False) 
    movement_type = models.CharField(max_length=50, choices=[(tag.name, tag.value) for tag in MovementType])
    quantity = models.IntegerField()
    reason = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inventory_movements"
        verbose_name = "Inventory Movement"
        verbose_name_plural = "Inventory Movements"
        app_label = "store"

    def __str__(self):
        return f"{self.movement_type} - {self.quantity}"
