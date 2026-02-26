from dataclasses import dataclass
from typing import List, Optional

@dataclass
class CreateHistoryInputDTO:
    """DTO for creating a history record."""
    is_healthy: bool
    title: str
    diagnosis: str
    confidence: float
    treatment: List[str]
    urgency_level: str
    photo: str

@dataclass
class HistoryOutputDTO:
    """DTO for returning a history record."""
    id: str
    is_healthy: bool
    title: str
    diagnosis: str
    confidence: float
    treatment: List[str]
    urgency_level: str
    photo: str
    created_at: str

@dataclass
class GetHistoryInputDTO:
    """DTO for requesting a history record."""
    id: str
