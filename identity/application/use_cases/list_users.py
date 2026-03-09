from typing import List
from injector import inject

from identity.application.dtos import UserOutputDTO
from identity.domain.interfaces import UserRepository
from ._helpers import _user_to_dto

class ListUsers:
    """Returns all registered users with their roles."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self) -> List[UserOutputDTO]:
        """Returns all users."""
        return [_user_to_dto(u) for u in self._repository.list_all()]
