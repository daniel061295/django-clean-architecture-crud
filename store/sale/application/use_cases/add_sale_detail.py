from uuid import UUID
from store.sale.domain.repositories import SaleRepository
from store.sale.application.dtos import AddSaleDetailDTO, SaleResponseDTO, SaleDetailResponseDTO

class AddSaleDetail:
    """
    Use case for adding a detail to a Sale.
    """

    def __init__(self, repository: SaleRepository):
        self.repository = repository

    def execute(self, dto: AddSaleDetailDTO) -> SaleResponseDTO:
        sale = self.repository.get_by_id(dto.sale_id)
        if not sale:
            raise ValueError(f"Sale with id {dto.sale_id} not found.")

        sale.add_detail(dto.plant_item_id, dto.quantity, dto.unit_price)
        saved_sale = self.repository.save(sale)

        return self._map_response(saved_sale)

    def _map_response(self, sale) -> SaleResponseDTO:
        # Duplicated mapping logic, helper method or mapper could be used better.
        # But keeping it simple here.
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
