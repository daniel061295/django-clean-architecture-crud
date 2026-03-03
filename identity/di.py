"""
Identity Dependency Injection Module.

Binds all identity domain interfaces to their Django ORM implementations.
"""
from injector import Binder, Module, provider, singleton

from billing.application.use_cases import AssignProSubscription, CreateFreeSubscriptionForNewUser

from identity.application.use_cases import (
    AssignPermissionToRole,
    AssignRoleToUser,
    CheckUserPermission,
    CreatePermission,
    CreateRole,
    CreateUser,
    DeleteUserAvatar,
    GetUser,
    GetUserPermissions,
    GetUserProfile,
    ListPermissions,
    ListRoles,
    ListUsers,
    RemoveRoleFromUser,
    UpdateUserAvatar,
    AuthenticateWithGoogle,
)
from identity.domain.interfaces import (
    GoogleAuthServiceInterface,
    PermissionRepository,
    RoleRepository,
    UserRepository,
)
from identity.infrastructure.repositories import (
    DjangoPermissionRepository,
    DjangoRoleRepository,
    DjangoUserRepository,
)
from identity.infrastructure.services.google_auth_service import GoogleAuthService


class IdentityModule(Module):
    """
    Dependency injection bindings for the Identity bounded context.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(PermissionRepository, to=DjangoPermissionRepository)
        binder.bind(RoleRepository, to=DjangoRoleRepository)
        binder.bind(UserRepository, to=DjangoUserRepository)
        binder.bind(GoogleAuthServiceInterface, to=GoogleAuthService)

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
        user_repository: UserRepository,
        create_free_subscription: CreateFreeSubscriptionForNewUser,
        assign_pro_subscription: AssignProSubscription,
    ) -> CreateUser:
        """Provides CreateUser use case with subscription assignment based on plan_name."""
        return CreateUser(role_repository, user_repository, create_free_subscription, assign_pro_subscription)

    @provider
    @singleton
    def provide_get_user_profile(self, repository: UserRepository) -> GetUserProfile:
        """Provides GetUserProfile use case."""
        return GetUserProfile(repository)

    @provider
    @singleton
    def provide_update_user_avatar(self, repository: UserRepository) -> UpdateUserAvatar:
        """Provides UpdateUserAvatar use case."""
        return UpdateUserAvatar(repository)

    @provider
    @singleton
    def provide_delete_user_avatar(self, repository: UserRepository) -> DeleteUserAvatar:
        """Provides DeleteUserAvatar use case."""
        return DeleteUserAvatar(repository)

    @provider
    def provide_authenticate_with_google(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        google_service: GoogleAuthServiceInterface,
        create_free_subscription: CreateFreeSubscriptionForNewUser,
    ) -> AuthenticateWithGoogle:
        """Provides AuthenticateWithGoogle use case."""
        return AuthenticateWithGoogle(
            user_repository, role_repository, google_service, create_free_subscription
        )
