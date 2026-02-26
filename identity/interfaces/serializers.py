"""
Identity Interface Serializers — DRF Serializers for RBAC REST endpoints.

These are dumb serializers: they only handle type conversion and format,
no business logic allowed here.
"""
from rest_framework import serializers


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
