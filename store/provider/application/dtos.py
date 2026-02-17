from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional

@dataclass
class CreateProviderDTO:
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None

@dataclass
class UpdateProviderDTO:
    id: UUID
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    active: Optional[bool] = None

@dataclass
class ProviderResponseDTO:
    id: UUID
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime
