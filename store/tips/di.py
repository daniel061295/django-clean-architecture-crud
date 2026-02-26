from injector import Module, provider, singleton

from store.tips.domain.interfaces import TipRepository
from store.tips.infrastructure.repositories import DjangoTipRepository
from store.tips.application.use_cases import (
    CreateTipUseCase, GetTipUseCase, GetAllTipsUseCase,
    UpdateTipUseCase, DeleteTipUseCase, GetRandomTipUseCase
)

class TipsModule(Module):
    """
    Dependency Injection module for the Tips entity.
    """
    
    @provider
    @singleton
    def provide_repository(self) -> TipRepository:
        return DjangoTipRepository()
        
    @provider
    def provide_create_use_case(self, repository: TipRepository) -> CreateTipUseCase:
        return CreateTipUseCase(repository)

    @provider
    def provide_get_use_case(self, repository: TipRepository) -> GetTipUseCase:
        return GetTipUseCase(repository)

    @provider
    def provide_get_all_use_case(self, repository: TipRepository) -> GetAllTipsUseCase:
        return GetAllTipsUseCase(repository)

    @provider
    def provide_get_random_use_case(self, repository: TipRepository) -> GetRandomTipUseCase:
        return GetRandomTipUseCase(repository)

    @provider
    def provide_update_use_case(self, repository: TipRepository) -> UpdateTipUseCase:
        return UpdateTipUseCase(repository)

    @provider
    def provide_delete_use_case(self, repository: TipRepository) -> DeleteTipUseCase:
        return DeleteTipUseCase(repository)
