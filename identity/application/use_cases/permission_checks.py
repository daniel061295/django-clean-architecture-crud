from injector import inject

from identity.application.dtos import GetUserPermissionsInputDTO, GetUserPermissionsOutputDTO, CheckUserPermissionInputDTO, CheckUserPermissionOutputDTO
from identity.domain.interfaces import UserRepository

class GetUserPermissions:
    """Returns all permission codes granted to a user through their roles."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: GetUserPermissionsInputDTO) -> GetUserPermissionsOutputDTO:
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            return GetUserPermissionsOutputDTO(permissions=[])

        permission_codes = list({p.code for role in user.roles for p in role.permissions})
        return GetUserPermissionsOutputDTO(permissions=permission_codes)

class CheckUserPermission:
    """Checks if a user has a specific permission through any of their roles."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: CheckUserPermissionInputDTO) -> CheckUserPermissionOutputDTO:
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            return CheckUserPermissionOutputDTO(has_permission=False)

        has_permission = user.has_permission(input_dto.permission_code)
        return CheckUserPermissionOutputDTO(has_permission=has_permission)
