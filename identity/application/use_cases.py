"""
Identity Application Use Cases — Business orchestration for RBAC management.

Each class handles a single, specific business action following the Command Pattern.
"""
from typing import List
from uuid import UUID

from injector import inject

from identity.application.dtos import (
    AssignPermissionToRoleInputDTO,
    AssignRoleToUserInputDTO,
    CheckUserPermissionInputDTO,
    CheckUserPermissionOutputDTO,
    CreatePermissionInputDTO,
    CreateRoleInputDTO,
    CreateUserInputDTO,
    GetUserPermissionsInputDTO,
    GetUserPermissionsOutputDTO,
    PermissionOutputDTO,
    RemoveRoleFromUserInputDTO,
    RoleOutputDTO,
    UserOutputDTO,
)
from identity.domain.entities import Permission, Role, User
from identity.domain.exceptions import (
    PermissionAlreadyExistsError,
    PermissionNotFoundError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
    UserNotFoundError,
)
from identity.domain.interfaces import PermissionRepository, RoleRepository, UserRepository
from identity.infrastructure.models import CustomUserModel


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _permission_to_dto(permission: Permission) -> PermissionOutputDTO:
    return PermissionOutputDTO(code=permission.code, description=permission.description)


def _role_to_dto(role: Role) -> RoleOutputDTO:
    return RoleOutputDTO(
        id=str(role.id),
        name=role.name,
        permissions=[_permission_to_dto(p) for p in role.permissions],
    )


def _user_to_dto(user: User) -> UserOutputDTO:
    return UserOutputDTO(
        id=str(user.id),
        email=user.email,
        username=user.username,
        is_active=user.is_active,
        roles=[_role_to_dto(r) for r in user.roles],
    )


# ---------------------------------------------------------------------------
# Permission Use Cases
# ---------------------------------------------------------------------------

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


class ListPermissions:
    """Returns all registered permissions."""

    @inject
    def __init__(self, repository: PermissionRepository) -> None:
        self._repository = repository

    def execute(self) -> List[PermissionOutputDTO]:
        """Returns a list of all permissions."""
        return [_permission_to_dto(p) for p in self._repository.list_all()]


# ---------------------------------------------------------------------------
# Role Use Cases
# ---------------------------------------------------------------------------

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


class ListRoles:
    """Returns all registered roles with their permissions."""

    @inject
    def __init__(self, repository: RoleRepository) -> None:
        self._repository = repository

    def execute(self) -> List[RoleOutputDTO]:
        """Returns a list of all roles."""
        return [_role_to_dto(r) for r in self._repository.list_all()]


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


# ---------------------------------------------------------------------------
# User Use Cases
# ---------------------------------------------------------------------------

class CreateUser:
    """Creates a new Django user and optionally assigns default roles."""

    @inject
    def __init__(self, role_repository: RoleRepository) -> None:
        self._role_repository = role_repository

    def execute(self, input_dto: CreateUserInputDTO) -> UserOutputDTO:
        """
        Creates a new user via Django's ORM and assigns roles by name.

        Args:
            input_dto: User creation data.

        Returns:
            UserOutputDTO: The created user.

        Raises:
            RoleNotFoundError: If any specified role name does not exist.
        """
        # Use Django's manager to safely hash the password
        user_model = CustomUserModel.objects.create_user(
            email=input_dto.email,
            username=input_dto.username,
            password=input_dto.password,
        )
        for role_name in input_dto.role_names:
            role = self._role_repository.get_by_name(role_name)
            if role is None:
                raise RoleNotFoundError(f"Role '{role_name}' does not exist.")
            from identity.infrastructure.models import RoleModel  # noqa: PLC0415
            role_model = RoleModel.objects.get(id=role.id)
            user_model.roles.add(role_model)

        # Re-fetch with relations
        from identity.infrastructure.mappers import UserMapper  # noqa: PLC0415
        from identity.infrastructure.models import CustomUserModel as M  # noqa: PLC0415
        refreshed = M.objects.prefetch_related("roles__permissions").get(id=user_model.id)
        return _user_to_dto(UserMapper.to_domain(refreshed))


class ListUsers:
    """Returns all registered users with their roles."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self) -> List[UserOutputDTO]:
        """Returns all users."""
        return [_user_to_dto(u) for u in self._repository.list_all()]


class GetUser:
    """Retrieves a single user by UUID."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID) -> UserOutputDTO:
        """
        Fetches a user by UUID.

        Args:
            user_id: The UUID of the user.

        Returns:
            UserOutputDTO: The user data.

        Raises:
            UserNotFoundError: If no user with this UUID exists.
        """
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User '{user_id}' not found.")
        return _user_to_dto(user)


class AssignRoleToUser:
    """Assigns a role to an existing user."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: AssignRoleToUserInputDTO) -> UserOutputDTO:
        """
        Assigns a role to a user.

        Args:
            input_dto: User UUID and Role UUID.

        Returns:
            UserOutputDTO: The updated user.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        if self._repository.get_by_id(input_dto.user_id) is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        updated = self._repository.assign_role(input_dto.user_id, input_dto.role_id)
        return _user_to_dto(updated)


class RemoveRoleFromUser:
    """Removes a role from an existing user."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: RemoveRoleFromUserInputDTO) -> UserOutputDTO:
        """
        Removes a role from a user.

        Args:
            input_dto: User UUID and Role UUID.

        Returns:
            UserOutputDTO: The updated user.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        if self._repository.get_by_id(input_dto.user_id) is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        updated = self._repository.remove_role(input_dto.user_id, input_dto.role_id)
        return _user_to_dto(updated)


# ---------------------------------------------------------------------------
# Permission Check Use Cases
# ---------------------------------------------------------------------------

class GetUserPermissions:
    """Returns all permission codes granted to a user through their roles."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: GetUserPermissionsInputDTO) -> GetUserPermissionsOutputDTO:
        """
        Returns all permission codes for a user.

        Args:
            input_dto: User UUID.

        Returns:
            GetUserPermissionsOutputDTO: List of permission codes.
        """
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
        """
        Checks if a user has a specific permission.

        Args:
            input_dto: User UUID and permission code.

        Returns:
            CheckUserPermissionOutputDTO: Whether the user has the permission.
        """
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            return CheckUserPermissionOutputDTO(has_permission=False)

        has_permission = user.has_permission(input_dto.permission_code)
        return CheckUserPermissionOutputDTO(has_permission=has_permission)
