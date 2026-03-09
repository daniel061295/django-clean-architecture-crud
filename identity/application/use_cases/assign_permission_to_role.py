from injector import inject

from identity.application.dtos import AssignPermissionToRoleInputDTO, RoleOutputDTO
from identity.domain.exceptions import PermissionNotFoundError, RoleNotFoundError
from identity.domain.interfaces import PermissionRepository, RoleRepository
from ._helpers import _role_to_dto


class AssignPermissionToRole:
    """Adds a permission to an existing role."""

    @inject
    def __init__(
        self,
        role_repository: RoleRepository,
        permission_repository: PermissionRepository,
    ) -> None:
        self._role_repository = role_repository
        self._permission_repository = permission_repository

    def execute(self, input_dto: AssignPermissionToRoleInputDTO) -> RoleOutputDTO:
        """
        Adds a permission to a role.

        Args:
            input_dto: Role ID and permission code.

        Returns:
            RoleOutputDTO: The updated role.

        Raises:
            RoleNotFoundError: If the role does not exist.
            PermissionNotFoundError: If the permission does not exist.
        """
        role = self._role_repository.get_by_id(input_dto.role_id)
        if role is None:
            raise RoleNotFoundError(f"Role '{input_dto.role_id}' not found.")

        if self._permission_repository.get_by_code(input_dto.permission_code) is None:
            raise PermissionNotFoundError(
                f"Permission '{input_dto.permission_code}' does not exist."
            )

        updated = self._role_repository.add_permission_to_role(
            input_dto.role_id, input_dto.permission_code
        )
        return _role_to_dto(updated)
