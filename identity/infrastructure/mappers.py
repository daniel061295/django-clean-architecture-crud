"""
Identity Infrastructure Mappers — Convert between ORM models and Domain entities.
"""
from uuid import UUID

from identity.domain.entities import Permission, Role, User
from identity.infrastructure.models import CustomUserModel, PermissionModel, RoleModel


class PermissionMapper:
    """Maps between PermissionModel (ORM) and Permission (Domain)."""

    @staticmethod
    def to_domain(model: PermissionModel) -> Permission:
        """Converts an ORM PermissionModel to a domain Permission."""
        return Permission(code=model.code, description=model.description)

    @staticmethod
    def to_db(permission: Permission) -> PermissionModel:
        """Converts a domain Permission to an ORM PermissionModel (not saved)."""
        return PermissionModel(code=permission.code, description=permission.description)


class RoleMapper:
    """Maps between RoleModel (ORM) and Role (Domain)."""

    @staticmethod
    def to_domain(model: RoleModel) -> Role:
        """
        Converts an ORM RoleModel to a domain Role, including permissions.

        Requires the model's permissions to be prefetched.
        """
        permissions = [
            PermissionMapper.to_domain(p) for p in model.permissions.all()
        ]
        return Role(id=model.id, name=model.name, permissions=permissions)


class UserMapper:
    """Maps between CustomUserModel (ORM) and User (Domain)."""

    @staticmethod
    def to_domain(model: CustomUserModel) -> User:
        """
        Converts an ORM CustomUserModel to a domain User, including roles and permissions.

        Requires roles__permissions to be prefetched.
        """
        roles = [RoleMapper.to_domain(r) for r in model.roles.all()]
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            roles=roles,
            is_active=model.is_active,
            avatar=model.avatar,
            auth_provider=model.auth_provider,
        )
