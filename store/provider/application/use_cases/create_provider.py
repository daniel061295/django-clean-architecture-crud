from store.provider.domain.entities import Provider
from store.provider.domain.repositories import ProviderRepository
from store.provider.application.dtos import CreateProviderDTO, ProviderResponseDTO

class CreateProvider:
    """
    Use case for creating a new Provider.
    """

    def __init__(self, repository: ProviderRepository):
        self.repository = repository

    def execute(self, dto: CreateProviderDTO) -> ProviderResponseDTO:
        # Note: Name is not unique in requirements, but we might want to check duplicate names if needed.
        # Strict requirements didn't say name must be unique, just required.
        # But let's check duplicates to be safe if that was implied by "similar to category"
        # The requirement only says "nombre (string, requerido)", unlike Category which said "único".
        # So I will NOT enforce uniqueness here unless specified. 
        # Wait, Category said "nombre (string, requerido, único)". Provider said "nombre (string, requerido)".
        # So no uniqueness check here.
        
        provider = Provider.create(
            name=dto.name,
            phone=dto.phone,
            email=dto.email,
            address=dto.address
        )
        saved_provider = self.repository.save(provider)

        return ProviderResponseDTO(
            id=saved_provider.id,
            name=saved_provider.name,
            phone=saved_provider.phone,
            email=saved_provider.email,
            address=saved_provider.address,
            active=saved_provider.active,
            created_at=saved_provider.created_at,
            updated_at=saved_provider.updated_at
        )
