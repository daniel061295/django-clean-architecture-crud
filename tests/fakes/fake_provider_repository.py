from typing import List, Optional, Tuple
from uuid import UUID
from store.provider.domain.entities import Provider
from store.provider.domain.repositories import ProviderRepository

class FakeProviderRepository(ProviderRepository):
    """
    In-memory implementation of ProviderRepository for testing.
    """

    def __init__(self):
        self.providers = {}

    def save(self, provider: Provider) -> Provider:
        self.providers[provider.id] = provider
        return provider

    def get_by_id(self, provider_id: UUID) -> Optional[Provider]:
        return self.providers.get(provider_id)
    
    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Provider], int]:
        all_providers = list(self.providers.values())
        
        # Simple filtering
        if filters.get("active") is not None:
             all_providers = [p for p in all_providers if p.active == filters["active"]]
            
        start = (page - 1) * page_size
        end = start + page_size
        return all_providers[start:end], len(all_providers)

    def delete(self, provider_id: UUID) -> None:
        if provider_id in self.providers:
            del self.providers[provider_id]
            
    def exists_by_name(self, name: str) -> bool:
        return any(p.name == name for p in self.providers.values())

    def exists_by_email(self, email: str) -> bool:
        return any(p.email == email for p in self.providers.values())
