from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional

@dataclass
class CreateCategoryDTO:
    name: str
    description: Optional[str] = None

@dataclass
class UpdateCategoryDTO:
    id: UUID
    name: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None

@dataclass
class CategoryResponseDTO:
    id: UUID
    name: str
    description: Optional[str]
    active: bool
    created_at: datetime
    updated_at: datetime
