import re
from identity.application.dtos import (
    PermissionOutputDTO,
    RoleOutputDTO,
    UserOutputDTO,
    MAX_AVATAR_SIZE_BYTES,
    ALLOWED_AVATAR_MIME_TYPES,
)
from identity.domain.entities import Permission, Role, User
from identity.domain.exceptions import AvatarValidationError
import base64

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
