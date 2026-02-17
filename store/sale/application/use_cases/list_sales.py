from typing import List, Tuple
from store.sale.domain.repositories import SaleRepository
from store.sale.application.dtos import SaleResponseDTO, SaleDetailResponseDTO

class ListSales:
    """
    Use case for listing Sales.
    """

    def __init__(self, repository: SaleRepository):
        self.repository = repository

    def execute(self, page: int, page_size: int, filters: dict) -> Tuple[List[SaleResponseDTO], int]:
        sales, total_count = self.repository.list(page, page_size, filters)
        
        dtos = []
        for sale in sales:
            details_dtos = [
                SaleDetailResponseDTO(
                    id=d.id,
                    plant_item_id=d.plant_item_id,
                    quantity=d.quantity,
                    unit_price=d.unit_price,
                    subtotal=d.subtotal
                )
                for d in sale.details
            ]
            dtos.append(
                SaleResponseDTO(
                    id=sale.id,
                    date=sale.date,
                    total=sale.total,
                    status=sale.status,
                    created_at=sale.created_at,
                    details=details_dtos
                )
            )
        
        return dtos, total_count
