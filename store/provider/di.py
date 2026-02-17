from injector import Module, provider, singleton
from store.provider.domain.repositories import ProviderRepository
from store.provider.infrastructure.repositories import DjangoProviderRepository
from store.provider.application.use_cases.create_provider import CreateProvider
from store.provider.application.use_cases.list_providers import ListProviders
from store.provider.application.use_cases.get_provider import GetProvider
from store.provider.application.use_cases.update_provider import UpdateProvider
from store.provider.application.use_cases.delete_provider import DeleteProvider

class ProviderModule(Module):
    @provider
    @singleton
    def provide_repository(self) -> ProviderRepository:
        return DjangoProviderRepository()

    @provider
    def provide_create_provider(self, repository: ProviderRepository) -> CreateProvider:
        return CreateProvider(repository)

    @provider
    def provide_list_providers(self, repository: ProviderRepository) -> ListProviders:
        return ListProviders(repository)

    @provider
    def provide_get_provider(self, repository: ProviderRepository) -> GetProvider:
        return GetProvider(repository)

    @provider
    def provide_update_provider(self, repository: ProviderRepository) -> UpdateProvider:
        return UpdateProvider(repository)

    @provider
    def provide_delete_provider(self, repository: ProviderRepository) -> DeleteProvider:
        return DeleteProvider(repository)
