from injector import Module, Binder
from store.history.domain.interfaces import HistoryRepository
from store.history.infrastructure.repositories import DjangoHistoryRepository

class HistoryModule(Module):
    """
    Dependency Injection Module for the History Entity.
    """
    def configure(self, binder: Binder):
        binder.bind(HistoryRepository, to=DjangoHistoryRepository)
