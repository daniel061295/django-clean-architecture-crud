from typing import List, Optional, Tuple
from uuid import UUID
from store.sale.domain.entities import Sale
from store.sale.domain.repositories import SaleRepository

class FakeSaleRepository(SaleRepository):
    """
    In-memory implementation of SaleRepository for testing.
    """

    def __init__(self):
        self.sales = {}

    def save(self, sale: Sale) -> Sale:
        self.sales[sale.id] = sale
        return sale

    def get_by_id(self, sale_id: UUID) -> Optional[Sale]:
        return self.sales.get(sale_id)
    
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Sale], int]:
        all_sales = list(self.sales.values())
        
        # Simple filtering
        if filters.get("status"):
            all_sales = [s for s in all_sales if s.status == filters["status"]]
            
        start = (page - 1) * page_size
        end = start + page_size
        return all_sales[start:end], len(all_sales)
