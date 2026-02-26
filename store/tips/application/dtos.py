from dataclasses import dataclass
from typing import Optional
import uuid

@dataclass
class CreateTipInputDTO:
    title: str
    description: str
    icon: str

@dataclass
class UpdateTipInputDTO:
    id: uuid.UUID
    title: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None

@dataclass
class TipOutputDTO:
    id: str
    title: str
    description: str
    icon: str
    created_at: str
