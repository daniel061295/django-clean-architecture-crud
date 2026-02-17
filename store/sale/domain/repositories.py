from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from store.sale.domain.entities import Sale

class SaleRepository(ABC):
    """
    Interface for Sale repository.
    """

    @abstractmethod
    def save(self, sale: Sale) -> Sale:
        pass

    @abstractmethod
    def get_by_id(self, sale_id: UUID) -> Optional[Sale]:
        pass
    
    @abstractmethod
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Sale], int]:
        pass
