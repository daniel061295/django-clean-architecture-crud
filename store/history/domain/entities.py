from dataclasses import dataclass, field
from typing import List, Optional
import uuid
from datetime import datetime

@dataclass(frozen=True)
class History:
    """
    Domain Entity representing the history of an AI plant health diagnosis.
    """
    is_healthy: bool
    title: str
    diagnosis: str
    confidence: float
    treatment: List[str]
    urgency_level: str
    photo: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.now)
