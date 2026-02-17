from uuid import UUID
from typing import Optional
from store.provider.domain.repositories import ProviderRepository
from store.provider.application.dtos import ProviderResponseDTO

class GetProvider:
    """
    Use case for retrieving a single Provider.
    """

    def __init__(self, repository: ProviderRepository):
        self.repository = repository

    def execute(self, provider_id: UUID) -> Optional[ProviderResponseDTO]:
        provider = self.repository.get_by_id(provider_id)
        if not provider:
            return None
            
        return ProviderResponseDTO(
            id=provider.id,
            name=provider.name,
            phone=provider.phone,
            email=provider.email,
            address=provider.address,
            active=provider.active,
            created_at=provider.created_at,
            updated_at=provider.updated_at
        )
