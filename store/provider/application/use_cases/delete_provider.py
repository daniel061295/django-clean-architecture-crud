from uuid import UUID
from store.provider.domain.repositories import ProviderRepository

class DeleteProvider:
    """
    Use case for deleting a Provider.
    """

    def __init__(self, repository: ProviderRepository):
        self.repository = repository

    def execute(self, provider_id: UUID) -> None:
        if not self.repository.get_by_id(provider_id):
             raise ValueError(f"Provider with id {provider_id} not found.")
             
        self.repository.delete(provider_id)
