from store.provider.domain.repositories import ProviderRepository
from store.provider.application.dtos import UpdateProviderDTO, ProviderResponseDTO

class UpdateProvider:
    """
    Use case for updating a Provider.
    """

    def __init__(self, repository: ProviderRepository):
        self.repository = repository

    def execute(self, dto: UpdateProviderDTO) -> ProviderResponseDTO:
        provider = self.repository.get_by_id(dto.id)
        if not provider:
            raise ValueError(f"Provider with id {dto.id} not found.")

        # Note: Name uniqueness is not enforced in Provider as per current implementation, 
        # but if we wanted to enforce it, we'd check here.

        provider.update(
            name=dto.name,
            phone=dto.phone,
            email=dto.email,
            address=dto.address,
            active=dto.active
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
