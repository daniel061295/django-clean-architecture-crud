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
                # Adjustment sets the stock to the quantity? OR adds/subtracts?
                # Usually "Ajuste" might mean "Correction". 
                # If quantity is just a positive number, it's ambiguous.
                # Common interpretation: 
                # Option A: Difference. Positive = add, Negative = subtract. (But entity says quantity > 0)
                # Option B: Set to specific value. (Movement quantity = New Stock?)
                # Option C: Just another type of add/subtract.
                # Given the requirements don't specify "Ajuste" behavior perfectly, 
                # but usually Ajuste implies correcting a discrepancy.
                # If I want to fix stock to 50, and it is 48, I add 2.
                # If I want to fix stock to 40, and it is 48, I subtract 8.
                # Since quantity > 0, maybe "AJUSTE" acts like ENTRADA/SALIDA regarding quantity?
                # Let's assume for this implementation that AJUSTE adds/subtracts if we invoke it like that.
                # OR maybe AJUSTE is typically used to SET the stock.
                # Let's assume for now AJUSTE acts as a generic addition/subtraction, 
                # BUT since I can't pass negative, I'll restrict AJUSTE to be...
                # Actually, standard inventory: 
                #  - Purchase -> IN
                #  - Sale -> OUT
                #  - Adjustment -> COULD BE IN OR OUT.
                # Since I only have one type "AJUSTE" and quantity > 0... 
                # I might need 2 types: AJUSTE_POSITIVO / AJUSTE_NEGATIVO?
                # The requirement just says "AJUSTE".
                # Let's treat AJUSTE as "Set Stock To Quantity" ? No, that loses history of "change".
                # Let's treat AJUSTE as "Add" for now, or maybe the user meant it as a catch-all.
                # I'll treat AJUSTE as adding stock for now (like a correction found). 
                # actually, to be safe, I'll treat it as ENTRADA for logic (add), 
                # but ideally we should have AJUSTE_IN and AJUSTE_OUT.
                # For this exercise, I'll assume AJUSTE is an absolute increase unless specified.
                # Wait, if I find less items, I need to remove.
                # I'll IMPLEMENT: AJUSTE simply adds for now. If user strictly needs to remove, 
                # they should use SALIDA with reason "Inventory Adjustment - Loss".
                # If they use AJUSTE, I'll assume it's finding extra items.
                plant_item.stock += dto.quantity 
            
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
