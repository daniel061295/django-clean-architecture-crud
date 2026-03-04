"""
Identity Interface Serializers — DRF Serializers for RBAC REST endpoints.

These are dumb serializers: they only handle type conversion and format,
no business logic allowed here.
"""
import base64
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from identity.application.dtos import (
    ALLOWED_AVATAR_MIME_TYPES,
    MAX_AVATAR_SIZE_BYTES,
)


# Regex pattern for valid base64 image with data URI scheme
BASE64_IMAGE_PATTERN = re.compile(
    r'^data:(?P<mime>image/(jpeg|png|webp));base64,[A-Za-z0-9+/]+=*$'
)


class UserAvatarBase64Field(serializers.CharField):
    """Custom field for validating base64 encoded avatar images."""
    
    def to_internal_value(self, data):
        """Validate the base64 image string."""
        if not isinstance(data, str):
            raise ValidationError("Avatar must be a string.")
        
        # Check size limit
        if len(data) > MAX_AVATAR_SIZE_BYTES * 4 // 3:
            raise ValidationError(
                f"Avatar size exceeds maximum of {MAX_AVATAR_SIZE_BYTES // 1024 // 1024}MB."
            )
        
        # Validate format
        match = BASE64_IMAGE_PATTERN.match(data)
        if not match:
            raise ValidationError(
                "Invalid image format. Must be data:image/jpeg;base64, data:image/png;base64, "
                "or data:image/webp;base64 followed by valid base64 data."
            )
        
        # Verify base64 can be decoded
        try:
            base64_data = data.split(',', 1)[1]
            base64.b64decode(base64_data, validate=True)
        except Exception:
            raise ValidationError("Invalid base64 encoding.")
        
        return data


# --- Permission Serializers ---

class PermissionInputSerializer(serializers.Serializer):
    """Deserializes permission creation requests."""

    code = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=255, required=False, default="")


class PermissionOutputSerializer(serializers.Serializer):
    """Serializes permission output DTOs."""

    code = serializers.CharField()
    description = serializers.CharField()


# --- Role Serializers ---

class RoleInputSerializer(serializers.Serializer):
    """Deserializes role creation requests."""

    name = serializers.CharField(max_length=100)
    permission_codes = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )


class AssignPermissionToRoleInputSerializer(serializers.Serializer):
    """Deserializes a request to assign a permission to a role."""

    permission_code = serializers.CharField(max_length=100)


class RoleOutputSerializer(serializers.Serializer):
    """Serializes role output DTOs including permissions."""

    id = serializers.CharField()
    name = serializers.CharField()
    permissions = PermissionOutputSerializer(many=True)


# --- User Serializers ---

class UserCreateInputSerializer(serializers.Serializer):
    """Deserializes user creation requests."""

    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    role_names = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    plan_name = serializers.CharField(
        required=False,
        default="FREE",
        help_text="Subscription plan: 'FREE' (permanent) or 'PRO' (30 days)"
    )
    avatar = UserAvatarBase64Field(required=False)

    def validate_plan_name(self, value):
        """Validate that plan_name is either FREE or PRO."""
        if value.upper() not in ["FREE", "PRO"]:
            raise serializers.ValidationError(
                "plan_name must be either 'FREE' or 'PRO'"
            )
        return value.upper()


class AssignRoleToUserInputSerializer(serializers.Serializer):
    """Deserializes a request to assign a role to a user."""

    role_id = serializers.UUIDField()


class UserOutputSerializer(serializers.Serializer):
    """Serializes user output DTOs including roles and permissions."""

    id = serializers.CharField()
    email = serializers.CharField()
    username = serializers.CharField()
    is_active = serializers.BooleanField()
    roles = RoleOutputSerializer(many=True)


# --- User Profile Serializers (for /me endpoint) ---

class UserProfileOutputSerializer(serializers.Serializer):
    """Serializes the current user's full profile."""

    id = serializers.CharField()
    email = serializers.CharField()
    username = serializers.CharField()
    is_active = serializers.BooleanField()
    avatar = serializers.CharField(allow_blank=True, required=False)
    roles = RoleOutputSerializer(many=True)
    permissions = serializers.ListField(child=serializers.CharField())


# --- User Avatar Serializers ---




class UserAvatarInputSerializer(serializers.Serializer):
    """Deserializes avatar upload requests."""

    avatar = UserAvatarBase64Field(required=True)


class UserAvatarOutputSerializer(serializers.Serializer):
    """Serializes avatar output DTOs."""

    avatar = serializers.CharField(allow_blank=True)


# --- Google Auth Serializers ---

class GoogleLoginInputSerializer(serializers.Serializer):
    """Deserializes Google OAuth login requests."""
    token = serializers.CharField(required=True)


# --- Password Management Serializers ---

class ChangePasswordInputSerializer(serializers.Serializer):
    """Deserializes requests to change password for an authenticated user."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class PasswordResetRequestInputSerializer(serializers.Serializer):
    """Deserializes requests to send a password reset email."""
    email = serializers.EmailField(required=True)


class PasswordResetConfirmInputSerializer(serializers.Serializer):
    """Deserializes requests to confirm a password reset with a token."""
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
