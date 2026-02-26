"""
Identity Dependency Injection Module.

Binds all identity domain interfaces to their Django ORM implementations.
"""
from injector import Binder, Module, provider, singleton

from identity.application.use_cases import (
    AssignPermissionToRole,
    AssignRoleToUser,
    CreatePermission,
    CreateRole,
    CreateUser,
    GetUser,
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
