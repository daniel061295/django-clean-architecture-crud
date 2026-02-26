"""
Identity Application DTOs — Input and Output transfer objects for identity use cases.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID


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
