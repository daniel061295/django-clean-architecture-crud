from typing import List
from injector import inject

from identity.application.dtos import PermissionOutputDTO
from identity.domain.interfaces import PermissionRepository
from ._helpers import _permission_to_dto

class ListPermissions:
    """Returns all registered permissions."""

    @inject
    def __init__(self, repository: PermissionRepository) -> None:
        self._repository = repository

    def execute(self) -> List[PermissionOutputDTO]:
        """Returns a list of all permissions."""
        return [_permission_to_dto(p) for p in self._repository.list_all()]
