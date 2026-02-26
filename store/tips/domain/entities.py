from dataclasses import dataclass, field
import uuid
from datetime import datetime

@dataclass
class Tip:
    """
    Domain Entity representing a gardening tip.
    """
    title: str
    description: str
    icon: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
