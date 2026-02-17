from django.db import transaction
from store.inventory_movement.domain.entities import InventoryMovement, MovementType
from store.inventory_movement.domain.repositories import InventoryMovementRepository
from store.inventory_movement.application.dtos import RegisterInventoryMovementDTO, InventoryMovementResponseDTO
from store.plant_item.domain.repositories import PlantItemRepository
from store.plant_item.domain.exceptions import PlantItemNotFoundError, InvalidStockError

class RegisterInventoryMovement:
    """
    Use case for registering an inventory movement and updating stock.
    """

    def __init__(self, 
                 movement_repository: InventoryMovementRepository,
                 plant_item_repository: PlantItemRepository):
        self.movement_repository = movement_repository
        self.plant_item_repository = plant_item_repository

    def execute(self, dto: RegisterInventoryMovementDTO) -> InventoryMovementResponseDTO:
        """
        Executes the use case for registering an inventory movement and updating stock.

        Args:
            dto: RegisterInventoryMovementDTO with the movement data.

        Returns:
            InventoryMovementResponseDTO with the registered movement data.
        """ 
        plant_item = self.plant_item_repository.get_by_id(dto.plant_item_id)
        if not plant_item:
            raise PlantItemNotFoundError(f"PlantItem with id {dto.plant_item_id} not found.")

        try:
            movement_type = MovementType(dto.movement_type)
        except ValueError:
            raise ValueError(f"Invalid movement type: {dto.movement_type}")

        # Validate logic: SALIDA cannot leave negative stock
        if movement_type == MovementType.SALIDA:
            if plant_item.stock < dto.quantity:
                raise InvalidStockError("Insufficient stock for this movement.")

        # Create movement entity
        movement = InventoryMovement.create(
            plant_item_id=dto.plant_item_id,
            movement_type=movement_type,
            quantity=dto.quantity,
            reason=dto.reason
        )

        # Execute in transaction
        with transaction.atomic():
            # Save movement
            saved_movement = self.movement_repository.save(movement)

            # Update PlantItem stock
            if movement_type == MovementType.ENTRADA:
                plant_item.stock += dto.quantity
            elif movement_type == MovementType.SALIDA:
                plant_item.stock -= dto.quantity
            elif movement_type == MovementType.AJUSTE:
                plant_item.stock = dto.quantity 
            
            plant_item.update(stock=plant_item.stock) # Triggers validation and availability update
            self.plant_item_repository.save(plant_item)

        return InventoryMovementResponseDTO(
            id=saved_movement.id,
            plant_item_id=saved_movement.plant_item_id,
            movement_type=saved_movement.movement_type.value,
            quantity=saved_movement.quantity,
            reason=saved_movement.reason,
            timestamp=saved_movement.timestamp,
            created_at=saved_movement.created_at
        )
