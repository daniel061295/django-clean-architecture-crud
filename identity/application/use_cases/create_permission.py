from typing import List
from injector import inject

from identity.application.dtos import CreatePermissionInputDTO, PermissionOutputDTO
from identity.domain.entities import Permission
from identity.domain.exceptions import PermissionAlreadyExistsError
from identity.domain.interfaces import PermissionRepository
from ._helpers import _permission_to_dto

class CreatePermission:
    """Creates a new system permission if the code does not already exist."""

    @inject
    def __init__(self, repository: PermissionRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: CreatePermissionInputDTO) -> PermissionOutputDTO:
        """
        Creates a new permission.

        Args:
            input_dto: Permission creation data.

        Returns:
            PermissionOutputDTO: The created permission.

        Raises:
            PermissionAlreadyExistsError: If the code is already registered.
        """
        if self._repository.exists_by_code(input_dto.code):
            raise PermissionAlreadyExistsError(
                f"Permission with code '{input_dto.code}' already exists."
            )
        permission = Permission(code=input_dto.code, description=input_dto.description)
        saved = self._repository.save(permission)
        return _permission_to_dto(saved)
