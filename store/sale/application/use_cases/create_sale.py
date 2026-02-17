from store.sale.domain.entities import Sale
from store.sale.domain.repositories import SaleRepository
from store.sale.application.dtos import CreateSaleDTO, SaleResponseDTO, SaleDetailResponseDTO

class CreateSale:
    """
    Use case for creating a new Sale.
    """

    def __init__(self, repository: SaleRepository):
        self.repository = repository

    def execute(self, dto: CreateSaleDTO) -> SaleResponseDTO:
        sale = Sale.create()
        
        for item in dto.initial_items:
            sale.add_detail(item.plant_item_id, item.quantity, item.unit_price)

        saved_sale = self.repository.save(sale)

        return self._map_response(saved_sale)
    
    def _map_response(self, sale: Sale) -> SaleResponseDTO:
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
