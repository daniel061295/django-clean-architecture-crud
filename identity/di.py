"""
Identity Dependency Injection Module.

Binds all identity domain interfaces to their Django ORM implementations.
"""
from injector import Binder, Module, provider, singleton

from billing.application.use_cases import CreateFreeSubscriptionForNewUser

from identity.application.use_cases import (
    AssignPermissionToRole,
    AssignRoleToUser,
    CheckUserPermission,
    CreatePermission,
    CreateRole,
    CreateUser,
    GetUser,
    GetUserPermissions,
    ListPermissions,
    ListRoles,
    ListUsers,
    RemoveRoleFromUser,
)
from identity.domain.interfaces import PermissionRepository, RoleRepository, UserRepository
from identity.infrastructure.repositories import (
    DjangoPermissionRepository,
    DjangoRoleRepository,
    DjangoUserRepository,
)


class IdentityModule(Module):
    """
    Dependency injection bindings for the Identity bounded context.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(PermissionRepository, to=DjangoPermissionRepository)
        binder.bind(RoleRepository, to=DjangoRoleRepository)
        binder.bind(UserRepository, to=DjangoUserRepository)

    @provider
    @singleton
    def provide_check_user_permission(self, repository: UserRepository) -> CheckUserPermission:
        """Provides CheckUserPermission use case."""
        return CheckUserPermission(repository)

    @provider
    @singleton
    def provide_get_user_permissions(self, repository: UserRepository) -> GetUserPermissions:
        """Provides GetUserPermissions use case."""
        return GetUserPermissions(repository)

    @provider
    def provide_create_user(
        self,
        role_repository: RoleRepository,
        create_free_subscription: CreateFreeSubscriptionForNewUser,
    ) -> CreateUser:
        """Provides CreateUser use case with automatic FREE subscription creation."""
        return CreateUser(role_repository, create_free_subscription)
