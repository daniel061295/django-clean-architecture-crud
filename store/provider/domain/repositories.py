from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID
from store.provider.domain.entities import Provider

class ProviderRepository(ABC):
    """
    Interface for Provider repository.
    """

    @abstractmethod
    def save(self, provider: Provider) -> Provider:
        pass

    @abstractmethod
    def get_by_id(self, provider_id: UUID) -> Optional[Provider]:
        pass
    
    @abstractmethod
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Provider], int]:
        pass

    @abstractmethod
    def delete(self, provider_id: UUID) -> None:
        pass
        
    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        pass
