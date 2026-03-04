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
    ChangeUserPassword,
    RequestPasswordReset,
    ConfirmPasswordReset,
)
from identity.domain.interfaces import (
    EmailServiceInterface,
    GoogleAuthServiceInterface,
    PasswordHasherInterface,
    PasswordTokenServiceInterface,
    PermissionRepository,
    RoleRepository,
    UserRepository,
)
from identity.infrastructure.repositories import (
    DjangoPermissionRepository,
    DjangoRoleRepository,
    DjangoUserRepository,
)
from core.domain.services import StorageServiceInterface
from core.infrastructure.services.r2_storage_service import CloudflareR2StorageService
from identity.infrastructure.services.resend_email_service import ResendEmailService
from identity.infrastructure.services.google_auth_service import GoogleAuthService
from identity.infrastructure.services.password_service import (
    DjangoPasswordHasher,
    DjangoPasswordTokenService,
)


class IdentityModule(Module):
    """
    Dependency injection bindings for the Identity bounded context.
    """

    def configure(self, binder: Binder) -> None:
        binder.bind(PermissionRepository, to=DjangoPermissionRepository)
        binder.bind(RoleRepository, to=DjangoRoleRepository)
        binder.bind(UserRepository, to=DjangoUserRepository)
        binder.bind(StorageServiceInterface, to=CloudflareR2StorageService)
        binder.bind(GoogleAuthServiceInterface, to=GoogleAuthService)
        binder.bind(EmailServiceInterface, to=ResendEmailService)
        binder.bind(PasswordHasherInterface, to=DjangoPasswordHasher)
        binder.bind(PasswordTokenServiceInterface, to=DjangoPasswordTokenService)

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
    def provide_get_user_profile(self, repository: UserRepository, storage_service: StorageServiceInterface) -> GetUserProfile:
        """Provides GetUserProfile use case."""
        return GetUserProfile(repository, storage_service)

    @provider
    @singleton
    def provide_update_user_avatar(self, repository: UserRepository, storage_service: StorageServiceInterface) -> UpdateUserAvatar:
        """Provides UpdateUserAvatar use case."""
        return UpdateUserAvatar(repository, storage_service)

    @provider
    @singleton
    def provide_delete_user_avatar(self, repository: UserRepository, storage_service: StorageServiceInterface) -> DeleteUserAvatar:
        """Provides DeleteUserAvatar use case."""
        return DeleteUserAvatar(repository, storage_service)

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

    @provider
    @singleton
    def provide_change_user_password(
        self,
        user_repository: UserRepository,
        hasher: PasswordHasherInterface,
    ) -> ChangeUserPassword:
        return ChangeUserPassword(user_repository, hasher)

    @provider
    @singleton
    def provide_request_password_reset(
        self,
        user_repository: UserRepository,
        token_service: PasswordTokenServiceInterface,
        email_service: EmailServiceInterface,
    ) -> RequestPasswordReset:
        return RequestPasswordReset(user_repository, token_service, email_service)

    @provider
    @singleton
    def provide_confirm_password_reset(
        self,
        user_repository: UserRepository,
        token_service: PasswordTokenServiceInterface,
        hasher: PasswordHasherInterface,
    ) -> ConfirmPasswordReset:
        return ConfirmPasswordReset(user_repository, token_service, hasher)
