"""
Identity Application Use Cases — Business orchestration for RBAC management.

Each class handles a single, specific business action following the Command Pattern.
"""
import base64
import re
from typing import List
from uuid import UUID

from injector import inject

from billing.application.use_cases import AssignProSubscription, CreateFreeSubscriptionForNewUser

from identity.application.dtos import (
    MAX_AVATAR_SIZE_BYTES,
    ALLOWED_AVATAR_MIME_TYPES,
    AssignPermissionToRoleInputDTO,
    AssignRoleToUserInputDTO,
    CheckUserPermissionInputDTO,
    CheckUserPermissionOutputDTO,
    CreatePermissionInputDTO,
    CreateRoleInputDTO,
    CreateUserInputDTO,
    DeleteUserAvatarInputDTO,
    GetUserPermissionsInputDTO,
    GetUserPermissionsOutputDTO,
    GetUserProfileInputDTO,
    PermissionOutputDTO,
    RemoveRoleFromUserInputDTO,
    RoleOutputDTO,
    UpdateUserAvatarInputDTO,
    UserAvatarOutputDTO,
    UserProfileOutputDTO,
    UserOutputDTO,
    AuthenticateWithGoogleInputDTO,
)
from identity.domain.entities import Permission, Role, User
from identity.domain.exceptions import (
    AvatarValidationError,
    PermissionAlreadyExistsError,
    PermissionNotFoundError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
    UserNotFoundError,
    UserAlreadyExistsError,
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
from core.domain.services import StorageServiceInterface
from identity.infrastructure.models import CustomUserModel
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


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
    """Creates a new Django user and assigns subscription based on plan_name."""

    @inject
    def __init__(
        self,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        create_free_subscription: CreateFreeSubscriptionForNewUser = None,
        assign_pro_subscription: AssignProSubscription = None,
    ) -> None:
        self._role_repository = role_repository
        self._user_repository = user_repository
        self._create_free_subscription = create_free_subscription
        self._assign_pro_subscription = assign_pro_subscription

    def execute(self, input_dto: CreateUserInputDTO) -> UserOutputDTO:
        """
        Creates a new user via Django's ORM and assigns subscription based on plan_name.
        - If plan_name="FREE" (default): Creates FREE subscription (permanent)
        - If plan_name="PRO": Creates PRO subscription (30 days)
        Assigns default avatar to the new user.

        Args:
            input_dto: User creation data with optional plan_name.

        Returns:
            UserOutputDTO: The created user.

        Raises:
            RoleNotFoundError: If any specified role name does not exist.
        """
        from identity.application.dtos import DEFAULT_USER_AVATAR  # noqa: PLC0415
        
        # Check if email already exists
        if self._user_repository.get_by_email(input_dto.email) is not None:
            raise UserAlreadyExistsError(f"El correo {input_dto.email} ya se encuentra registrado.")

        avatar_to_use = input_dto.avatar if input_dto.avatar else DEFAULT_USER_AVATAR

        # Use Django's manager to safely hash the password
        user_model = CustomUserModel.objects.create_user(
            email=input_dto.email,
            username=input_dto.username,
            password=input_dto.password,
            avatar=avatar_to_use,  # Set default avatar or custom
        )
        for role_name in input_dto.role_names:
            role = self._role_repository.get_by_name(role_name)
            if role is None:
                raise RoleNotFoundError(f"Role '{role_name}' does not exist.")
            from identity.infrastructure.models import RoleModel  # noqa: PLC0415
            role_model = RoleModel.objects.get(id=role.id)
            user_model.roles.add(role_model)

        # Create subscription based on plan_name
        if input_dto.plan_name.upper() == "PRO":
            # Assign PRO subscription (cancels any existing FREE)
            if self._assign_pro_subscription is not None:
                from billing.application.use_cases import AssignProSubscription  # noqa: PLC0415
                self._assign_pro_subscription.execute(user_model.id)
        else:
            # Create FREE subscription (permanent, default)
            if self._create_free_subscription is not None:
                from billing.application.dtos import CreateFreeSubscriptionForUserInputDTO  # noqa: PLC0415
                free_sub_dto = CreateFreeSubscriptionForUserInputDTO(user_id=user_model.id)
                self._create_free_subscription.execute(free_sub_dto)

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


class AuthenticateWithGoogle:
    """Authenticates a user via Google OAuth, creating a new local user if they don't exist."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        google_service: GoogleAuthServiceInterface,
        create_free_subscription: CreateFreeSubscriptionForNewUser = None,
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._google_service = google_service
        self._create_free_subscription = create_free_subscription

    def execute(self, input_dto: AuthenticateWithGoogleInputDTO) -> UserOutputDTO:
        # Verify token
        payload = self._google_service.verify_google_token(input_dto.token)
        email = payload.get("email")
        if not email:
            raise ValueError("Google token did not contain an email address.")

        user = self._user_repository.get_by_email(email)
        if user is None:
            # Create user in Django
            from identity.infrastructure.models import CustomUserModel, RoleModel
            from identity.application.dtos import DEFAULT_USER_AVATAR
            
            # Using email as username base to keep it simple
            username = email.split("@")[0]
            
            user_model = CustomUserModel.objects.create_user(
                email=email,
                username=username,
                password=None,  # No password for Google users
                avatar=payload.get("picture", DEFAULT_USER_AVATAR),
                auth_provider="google"
            )
            
            # They should be 'free_user' with FREE sub initially
            role = self._role_repository.get_by_name("free_user")
            if role:
                role_model = RoleModel.objects.get(id=role.id)
                user_model.roles.add(role_model)
                
            if self._create_free_subscription:
                from billing.application.dtos import CreateFreeSubscriptionForUserInputDTO
                free_sub_dto = CreateFreeSubscriptionForUserInputDTO(user_id=user_model.id)
                self._create_free_subscription.execute(free_sub_dto)
            
            from identity.infrastructure.mappers import UserMapper
            refreshed = CustomUserModel.objects.prefetch_related("roles__permissions").get(id=user_model.id)
            user = UserMapper.to_domain(refreshed)

        return _user_to_dto(user)


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


# ---------------------------------------------------------------------------
# User Profile Use Cases (for /me endpoint)
# ---------------------------------------------------------------------------

class GetUserProfile:
    """Returns the full profile of a user including avatar, roles, and permissions."""

    @inject
    def __init__(self, repository: UserRepository, storage_service: StorageServiceInterface) -> None:
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: GetUserProfileInputDTO) -> UserProfileOutputDTO:
        """
        Returns the full profile of a user.

        Args:
            input_dto: User UUID.

        Returns:
            UserProfileOutputDTO: User profile with avatar, roles, and permissions.
        """
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        permission_codes = list({p.code for role in user.roles for p in role.permissions})
        
        avatar_url = user.avatar
        if avatar_url and not avatar_url.startswith("data:image") and avatar_url != "":
            # Generate Signed URL for R2 objects
            avatar_url = self._storage_service.get_signed_url(user.avatar) or user.avatar

        return UserProfileOutputDTO(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            avatar=avatar_url,
            roles=[_role_to_dto(r) for r in user.roles],
            permissions=permission_codes,
        )


# ---------------------------------------------------------------------------
# User Avatar Use Cases
# ---------------------------------------------------------------------------

# Regex pattern for valid base64 image with data URI scheme
BASE64_IMAGE_PATTERN = re.compile(
    r'^data:(?P<mime>image/(jpeg|png|webp));base64,[A-Za-z0-9+/]+=*$'
)


def _validate_avatar_base64(avatar_base64: str) -> str:
    """
    Validates a base64 encoded avatar image.
    
    Args:
        avatar_base64: The base64 string with data URI scheme.
        
    Returns:
        The MIME type of the image.
        
    Raises:
        AvatarValidationError: If the avatar is invalid.
    """
    if not avatar_base64:
        raise AvatarValidationError("Avatar cannot be empty.")
    
    # Check size limit (base64 is ~33% larger than binary)
    if len(avatar_base64) > MAX_AVATAR_SIZE_BYTES * 4 // 3:
        raise AvatarValidationError(
            f"Avatar size exceeds maximum of {MAX_AVATAR_SIZE_BYTES // 1024 // 1024}MB."
        )
    
    # Validate format with regex
    match = BASE64_IMAGE_PATTERN.match(avatar_base64)
    if not match:
        raise AvatarValidationError(
            "Invalid image format. Must be data:image/jpeg;base64, data:image/png;base64, "
            "or data:image/webp;base64 followed by valid base64 data."
        )
    
    mime_type = match.group('mime')
    if mime_type not in ALLOWED_AVATAR_MIME_TYPES:
        raise AvatarValidationError(
            f"Image type '{mime_type}' not allowed. Allowed types: {', '.join(ALLOWED_AVATAR_MIME_TYPES)}"
        )
    
    # Verify base64 can be decoded
    try:
        base64_data = avatar_base64.split(',', 1)[1]
        base64.b64decode(base64_data, validate=True)
    except Exception:
        raise AvatarValidationError("Invalid base64 encoding.")
    
    return mime_type


class UpdateUserAvatar:
    """Updates a user's avatar image."""

    @inject
    def __init__(self, repository: UserRepository, storage_service: StorageServiceInterface) -> None:
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: UpdateUserAvatarInputDTO) -> UserAvatarOutputDTO:
        """
        Updates the user's avatar image.

        Args:
            input_dto: User UUID and avatar base64 string.

        Returns:
            UserAvatarOutputDTO: The updated avatar.

        Raises:
            UserNotFoundError: If the user does not exist.
            AvatarValidationError: If the avatar is invalid.
        """
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")
        
        # Validate the base64 avatar
        _validate_avatar_base64(input_dto.avatar_base64)

        import base64
        from core.utils.images import optimize_image

        base64_data = input_dto.avatar_base64.split(',', 1)[1]
        raw_bytes = base64.b64decode(base64_data)
        optimized_bytes = optimize_image(raw_bytes, max_size=(500, 500), quality=80)

        # Upload to R2 Storage
        file_name = f"avatars/{input_dto.user_id}.jpg"
        r2_key = self._storage_service.upload_file(optimized_bytes, file_name, "image/jpeg")

        if user.avatar and not user.avatar.startswith("data:image"):
            try:
                self._storage_service.delete_file(user.avatar)
            except Exception:
                pass

        updated_user = self._repository.update_avatar(input_dto.user_id, r2_key)
        signed_url = self._storage_service.get_signed_url(updated_user.avatar) or updated_user.avatar

        return UserAvatarOutputDTO(avatar=signed_url)


class DeleteUserAvatar:
    """Deletes a user's avatar image."""

    @inject
    def __init__(self, repository: UserRepository, storage_service: StorageServiceInterface) -> None:
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: DeleteUserAvatarInputDTO) -> UserAvatarOutputDTO:
        """
        Deletes the user's avatar image.

        Args:
            input_dto: User UUID.

        Returns:
            UserAvatarOutputDTO: Empty avatar string.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        if user.avatar and not user.avatar.startswith("data:image"):
            try:
                self._storage_service.delete_file(user.avatar)
            except Exception:
                pass

        updated_user = self._repository.delete_avatar(input_dto.user_id)
        # Assuming delete_avatar sets avatar back to the default fallback (which is likely a base64 encoded image starting with data:image)
        return UserAvatarOutputDTO(avatar=updated_user.avatar)


# ---------------------------------------------------------------------------
# Password Management Use Cases
# ---------------------------------------------------------------------------

class ChangeUserPassword:
    """Changes the password for an authenticated user."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherInterface,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, input_dto: "ChangeUserPasswordInputDTO") -> None:
        from identity.domain.exceptions import InvalidPasswordError
        
        user = self._user_repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        # Let's get the hashed password from db model
        from identity.infrastructure.models import CustomUserModel
        user_model = CustomUserModel.objects.get(id=input_dto.user_id)
        
        if not self._password_hasher.check_password(input_dto.old_password, user_model.password):
            raise InvalidPasswordError("La contraseña actual es incorrecta.")

        hashed_new_password = self._password_hasher.make_password(input_dto.new_password)
        self._user_repository.update_password(input_dto.user_id, hashed_new_password)


class RequestPasswordReset:
    """Handles requesting a password reset and sending the email."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: PasswordTokenServiceInterface,
        email_service: EmailServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service
        self._email_service = email_service

    def execute(self, input_dto: "RequestPasswordResetInputDTO", frontend_url: str) -> None:
        user = self._user_repository.get_by_email(input_dto.email)
        if user is None:
            # We return silently to prevent email enumeration attacks
            return

        token = self._token_service.generate_token(user.id)
        if not token:
            return
            
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        
        # Build the final URL (Assuming frontend_url already has the domain like http://localhost:3000/reset-password)
        reset_link = f"{frontend_url}?uid={uidb64}&token={token}"
        
        self._email_service.send_password_reset_email(user.email, reset_link)


class ConfirmPasswordReset:
    """Confirms and executes a password reset."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: PasswordTokenServiceInterface,
        password_hasher: PasswordHasherInterface,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service
        self._password_hasher = password_hasher

    def execute(self, input_dto: "ConfirmPasswordResetInputDTO") -> None:
        from identity.domain.exceptions import InvalidTokenError
        
        user = self._user_repository.get_by_id(input_dto.user_id)
        if user is None:
            raise InvalidTokenError("El token es inválido o ha expirado.")

        if not self._token_service.validate_token(input_dto.user_id, input_dto.token):
            raise InvalidTokenError("El token es inválido o ha expirado.")

        hashed_password = self._password_hasher.make_password(input_dto.new_password)
        self._user_repository.update_password(input_dto.user_id, hashed_password)
