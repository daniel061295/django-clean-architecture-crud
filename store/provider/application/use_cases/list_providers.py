from typing import List, Tuple
from store.provider.domain.repositories import ProviderRepository
from store.provider.application.dtos import ProviderResponseDTO

class ListProviders:
    """
    Use case for listing Providers.
    """

    def __init__(self, repository: ProviderRepository):
        self.repository = repository

    def execute(self, page: int, page_size: int, filters: dict) -> Tuple[List[ProviderResponseDTO], int]:
        providers, total_count = self.repository.list(page, page_size, filters)
        
        dtos = [
            ProviderResponseDTO(
                id=p.id,
                name=p.name,
                phone=p.phone,
                email=p.email,
                address=p.address,
                active=p.active,
                created_at=p.created_at,
                updated_at=p.updated_at
            )
            for p in providers
        ]
        
        return dtos, total_count
