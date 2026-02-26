"""
Identity Domain Exceptions — Pure Python, no framework dependencies.
"""
from store.plant_item.domain.exceptions import DomainError


class UserNotFoundError(DomainError):
    """Raised when a user cannot be found by the given identifier."""


class RoleNotFoundError(DomainError):
    """Raised when a role cannot be found by the given identifier."""


class PermissionNotFoundError(DomainError):
    """Raised when a permission cannot be found by the given code."""


class PermissionDeniedError(DomainError):
    """Raised when a user attempts an action they are not permitted to perform."""


class RoleAlreadyExistsError(DomainError):
    """Raised when attempting to create a role with a name that already exists."""


class PermissionAlreadyExistsError(DomainError):
    """Raised when attempting to create a permission with a code that already exists."""
