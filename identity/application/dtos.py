"""
Identity Application DTOs — Input and Output transfer objects for identity use cases.
"""
from dataclasses import dataclass, field
from typing import List
from uuid import UUID

from identity.utils import get_default_user_avatar


# Function to get default avatar (called at runtime)
DEFAULT_USER_AVATAR = get_default_user_avatar()


# --- Permission DTOs ---

@dataclass
class CreatePermissionInputDTO:
    """Input DTO for the CreatePermission use case."""
    code: str
    description: str = ""


@dataclass
class PermissionOutputDTO:
    """Output DTO representing a single permission."""
    code: str
    description: str


# --- Role DTOs ---

@dataclass
class CreateRoleInputDTO:
    """Input DTO for the CreateRole use case."""
    name: str
    permission_codes: List[str] = field(default_factory=list)


@dataclass
class AssignPermissionToRoleInputDTO:
    """Input DTO for the AssignPermissionToRole use case."""
    role_id: UUID
    permission_code: str


@dataclass
class RoleOutputDTO:
    """Output DTO representing a role with its permissions."""
    id: str
    name: str
    permissions: List[PermissionOutputDTO] = field(default_factory=list)


# --- User DTOs ---

@dataclass
class CreateUserInputDTO:
    """Input DTO for the CreateUser use case."""
    email: str
    username: str
    password: str
    role_names: List[str] = field(default_factory=list)
    plan_name: str = "FREE"  # Default to FREE, can be "PRO"
    avatar: str | None = None


@dataclass
class AssignRoleToUserInputDTO:
    """Input DTO for the AssignRoleToUser use case."""
    user_id: UUID
    role_id: UUID


@dataclass
class RemoveRoleFromUserInputDTO:
    """Input DTO for the RemoveRoleFromUser use case."""
    user_id: UUID
    role_id: UUID


@dataclass
class UserOutputDTO:
    """Output DTO representing a user with their roles."""
    id: str
    email: str
    username: str
    is_active: bool
    roles: List[RoleOutputDTO] = field(default_factory=list)


# --- Permission Check DTOs ---

@dataclass
class GetUserPermissionsInputDTO:
    """Input DTO for the GetUserPermissions use case."""
    user_id: UUID


@dataclass
class GetUserPermissionsOutputDTO:
    """Output DTO representing all permissions granted to a user."""
    permissions: List[str] = field(default_factory=list)


@dataclass
class CheckUserPermissionInputDTO:
    """Input DTO for the CheckUserPermission use case."""
    user_id: UUID
    permission_code: str


@dataclass
class CheckUserPermissionOutputDTO:
    """Output DTO indicating whether a user has a specific permission."""
    has_permission: bool


# --- User Profile DTOs (for /me endpoint) ---

@dataclass
class GetUserProfileInputDTO:
    """Input DTO for the GetUserProfile use case."""
    user_id: UUID


@dataclass
class UserProfileOutputDTO:
    """Output DTO representing the current user's full profile."""
    id: str
    email: str
    username: str
    is_active: bool
    avatar: str  # Base64 encoded image
    roles: List[RoleOutputDTO] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)


# --- User Avatar DTOs ---

# Maximum avatar size: 5 MB (file) ≈ 6.7 MB in base64
MAX_AVATAR_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_AVATAR_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]


@dataclass
class UpdateUserAvatarInputDTO:
    """Input DTO for the UpdateUserAvatar use case."""
    user_id: UUID
    avatar_base64: str  # data:image/...;base64,...


@dataclass
class DeleteUserAvatarInputDTO:
    """Input DTO for the DeleteUserAvatar use case."""
    user_id: UUID


@dataclass
class UserAvatarOutputDTO:
    """Output DTO representing the user's avatar URL."""
    avatar: str  # Base64 string or empty string


# --- Google Auth DTOs ---

@dataclass
class AuthenticateWithGoogleInputDTO:
    """Input DTO for the AuthenticateWithGoogle use case."""
    token: str


# --- Password Management DTOs ---

@dataclass
class ChangeUserPasswordInputDTO:
    """Input DTO for the ChangeUserPassword use case."""
    user_id: UUID
    old_password: str
    new_password: str


@dataclass
class RequestPasswordResetInputDTO:
    """Input DTO for the RequestPasswordReset use case."""
    email: str


@dataclass
class ConfirmPasswordResetInputDTO:
    """Input DTO for the ConfirmPasswordReset use case."""
    user_id: UUID
    token: str
    new_password: str
