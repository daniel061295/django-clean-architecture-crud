from typing import List
from injector import inject

from identity.application.dtos import RoleOutputDTO
from identity.domain.interfaces import RoleRepository
from ._helpers import _role_to_dto

class ListRoles:
    """Returns all registered roles with their permissions."""

    @inject
    def __init__(self, repository: RoleRepository) -> None:
        self._repository = repository

    def execute(self) -> List[RoleOutputDTO]:
        """Returns a list of all roles."""
        return [_role_to_dto(r) for r in self._repository.list_all()]
