from typing import List
from injector import inject

from identity.application.dtos import CreateRoleInputDTO, RoleOutputDTO
from identity.domain.entities import Permission, Role
from identity.domain.exceptions import PermissionNotFoundError, RoleAlreadyExistsError
from identity.domain.interfaces import PermissionRepository, RoleRepository
from ._helpers import _role_to_dto

class CreateRole:
    """Creates a new role, optionally assigning existing permissions by code."""

    @inject
    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ) -> None:
        self._role_repository = role_repository
        self._permission_repository = permission_repository

    def execute(self, input_dto: CreateRoleInputDTO) -> RoleOutputDTO:
        """
        Creates a new role.

        Args:
            input_dto: Role name and optional permission codes.

        Returns:
            RoleOutputDTO: The created role with its permissions.

        Raises:
            RoleAlreadyExistsError: If the role name is taken.
            PermissionNotFoundError: If any permission code does not exist.
        """
        if self._role_repository.exists_by_name(input_dto.name):
            raise RoleAlreadyExistsError(f"Role '{input_dto.name}' already exists.")

        permissions: List[Permission] = []
        for code in input_dto.permission_codes:
            perm = self._permission_repository.get_by_code(code)
            if perm is None:
                raise PermissionNotFoundError(f"Permission '{code}' does not exist.")
            permissions.append(perm)

        role = Role.create(name=input_dto.name, permissions=permissions)
        saved = self._role_repository.save(role)
        return _role_to_dto(saved)
