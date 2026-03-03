"""
Identity Domain Entities — Pure Python, no framework dependencies.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List
from uuid import UUID


@dataclass(frozen=True)
class Permission:
    """
    Value Object representing a single permission in the RBAC system.

    Attributes:
        code: Unique identifier string for this permission (e.g. 'scan_plant').
        description: Human-readable description.
    """

    code: str
    description: str = ""

    def __post_init__(self) -> None:
        if not self.code or not self.code.strip():
            raise ValueError("Permission code cannot be empty.")


@dataclass
class Role:
    """
    Entity representing a named role that groups a set of permissions.

    Attributes:
        id: Unique identifier.
        name: Human-readable role name (e.g. 'admin', 'subscriber').
        permissions: List of permissions assigned to this role.
    """

    id: UUID
    name: str
    permissions: List[Permission] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Role name cannot be empty.")

    def has_permission(self, permission_code: str) -> bool:
        """
        Returns True if this role grants the given permission code.

        Args:
            permission_code: The permission code to check.

        Returns:
            bool: True if the role grants the permission, False otherwise.
        """
        return any(p.code == permission_code for p in self.permissions)

    @classmethod
    def create(cls, name: str, permissions: Optional[List[Permission]] = None) -> "Role":
        """
        Factory method to create a new Role with a generated UUID.

        Args:
            name: Name of the role.
            permissions: Initial list of permissions.

        Returns:
            A new Role entity.
        """
        return cls(id=uuid.uuid4(), name=name, permissions=permissions or [])


@dataclass
class User:
    """
    Domain Entity representing an authenticated user in the system.

    This entity carries only what the domain needs. It does NOT contain
    password hashes or any framework-specific fields.

    Attributes:
        id: Unique identifier.
        email: User email address (used as login).
        username: Optional username.
        roles: List of roles assigned to this user.
        is_active: Whether the user account is active.
        avatar: Base64 encoded image string (data:image/...;base64,...).
    """

    id: UUID
    email: str
    username: str
    roles: List[Role] = field(default_factory=list)
    is_active: bool = True
    avatar: str = ""
    auth_provider: str = "local"

    def has_permission(self, permission_code: str) -> bool:
        """
        Returns True if any assigned role grants the given permission.

        Args:
            permission_code: The permission code to check (e.g. 'scan_plant').

        Returns:
            bool: True if the user has the permission through any role.
        """
        return any(role.has_permission(permission_code) for role in self.roles)

    @classmethod
    def create(cls, email: str, username: str, auth_provider: str = "local") -> "User":
        """
        Factory method to create a new User with a generated UUID.

        Args:
            email: User email address.
            username: User username.
            auth_provider: Provider used to create the user (e.g. 'local', 'google').

        Returns:
            A new User entity.
        """
        return cls(id=uuid.uuid4(), email=email, username=username, auth_provider=auth_provider)
