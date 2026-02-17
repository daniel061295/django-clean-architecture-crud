from uuid import UUID
from django.db import transaction
from store.sale.domain.repositories import SaleRepository
from store.sale.application.dtos import SaleResponseDTO, SaleDetailResponseDTO
from store.inventory_movement.application.use_cases.register_inventory_movement import RegisterInventoryMovement
from store.inventory_movement.application.dtos import RegisterInventoryMovementDTO
from store.inventory_movement.domain.entities import MovementType

class CompleteSale:
    """
    Use case for completing a Sale and triggering inventory updates.
    """

    def __init__(self, 
                 sale_repository: SaleRepository,
                 register_inventory_movement: RegisterInventoryMovement):
        self.sale_repository = sale_repository
        self.register_inventory_movement = register_inventory_movement

    def execute(self, sale_id: UUID) -> SaleResponseDTO:
        sale = self.sale_repository.get_by_id(sale_id)
        if not sale:
            raise ValueError(f"Sale with id {sale_id} not found.")

        # Business Logic
        # 1. Update status
        sale.complete()

        with transaction.atomic():
            # 2. Save sale state
            saved_sale = self.sale_repository.save(sale)

            # 3. Create inventory movements for each detail
            for detail in saved_sale.details:
                movement_dto = RegisterInventoryMovementDTO(
                    plant_item_id=detail.plant_item_id,
                    movement_type=MovementType.SALIDA.name,
                    quantity=detail.quantity,
                    reason=f"Sale Completion - Sale {saved_sale.id}"
                )
                self.register_inventory_movement.execute(movement_dto)

        return self._map_response(saved_sale)

    def _map_response(self, sale) -> SaleResponseDTO:
        details_dto = [
            SaleDetailResponseDTO(
                id=d.id,
                plant_item_id=d.plant_item_id,
                quantity=d.quantity,
                unit_price=d.unit_price,
                subtotal=d.subtotal
            ) for d in sale.details
        ]
        
        return SaleResponseDTO(
            id=sale.id,
            date=sale.date,
            total=sale.total,
            status=sale.status.value,
            created_at=sale.created_at,
            details=details_dto
        )
