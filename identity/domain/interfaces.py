"""
Identity Domain Repository Interfaces (Ports) — Pure Python ABCs.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from identity.domain.entities import Permission, Role, User


class PermissionRepository(ABC):
    """Abstract interface for Permission data access."""

    @abstractmethod
    def save(self, permission: Permission) -> Permission:
        """Saves a permission and returns the persisted instance."""

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[Permission]:
        """Retrieves a permission by its unique code. Returns None if not found."""

    @abstractmethod
    def list_all(self) -> List[Permission]:
        """Returns all permissions."""

    @abstractmethod
    def exists_by_code(self, code: str) -> bool:
        """Returns True if a permission with the given code already exists."""


class RoleRepository(ABC):
    """Abstract interface for Role data access."""

    @abstractmethod
    def save(self, role: Role) -> Role:
        """Saves a role (with its permissions) and returns the persisted instance."""

    @abstractmethod
    def get_by_id(self, role_id: UUID) -> Optional[Role]:
        """Retrieves a role by its UUID. Returns None if not found."""

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Role]:
        """Retrieves a role by its name. Returns None if not found."""

    @abstractmethod
    def list_all(self) -> List[Role]:
        """Returns all roles with their permissions."""

    @abstractmethod
    def exists_by_name(self, name: str) -> bool:
        """Returns True if a role with the given name already exists."""

    @abstractmethod
    def add_permission_to_role(self, role_id: UUID, permission_code: str) -> Role:
        """Adds a permission to a role. Returns the updated role."""


class UserRepository(ABC):
    """Abstract interface for User data access."""

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieves a user by UUID, including their roles and permissions."""

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user by email address."""

    @abstractmethod
    def list_all(self) -> List[User]:
        """Returns all users."""

    @abstractmethod
    def assign_role(self, user_id: UUID, role_id: UUID) -> User:
        """Assigns a role to a user. Returns the updated user entity."""

    @abstractmethod
    def remove_role(self, user_id: UUID, role_id: UUID) -> User:
        """Removes a role from a user. Returns the updated user entity."""

    @abstractmethod
    def update_avatar(self, user_id: UUID, avatar_base64: str) -> User:
        """Updates the user's avatar with a base64 encoded image. Returns the updated user entity."""

    @abstractmethod
    def delete_avatar(self, user_id: UUID) -> User:
        """Deletes the user's avatar image. Returns the updated user entity."""

    @abstractmethod
    def update_password(self, user_id: UUID, hashed_password: str) -> None:
        """Updates the user's password hash in the database."""


class PasswordHasherInterface(ABC):
    """Abstract interface for password hashing."""

    @abstractmethod
    def make_password(self, password: str) -> str:
        """Hashes a plain text password."""

    @abstractmethod
    def check_password(self, password: str, encoded: str) -> bool:
        """Verifies a plain text password against a hash. Returns True if they match."""


class PasswordTokenServiceInterface(ABC):
    """Abstract interface for generating and validating short-lived secure tokens."""

    @abstractmethod
    def generate_token(self, user_id: UUID) -> str:
        """Generates a secure password reset token for the given user."""

    @abstractmethod
    def validate_token(self, user_id: UUID, token: str) -> bool:
        """Validates if the provided token is valid and not expired for the given user."""


class EmailServiceInterface(ABC):
    """Abstract interface for sending transactional emails."""

    @abstractmethod
    def send_password_reset_email(self, to_email: str, reset_link: str) -> None:
        """Sends an email containing the password reset link."""


class GoogleAuthServiceInterface(ABC):
    """Abstract interface for Google Auth verification service."""

    @abstractmethod
    def verify_google_token(self, token: str) -> dict:
        """
        Verifies a Google OAuth token.

        Args:
            token: The Google JWT token.

        Returns:
            dict: The decoded token payload containing email, given_name, etc.
            
        Raises:
            ValueError: If the token is invalid.
        """
