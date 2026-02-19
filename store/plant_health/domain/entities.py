from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class PlantHealthReport:
    """
    Domain Entity representing the health diagnosis of a plant.
    """
    is_healthy: bool
    diagnosis: str
    confidence: float
    treatment: List[str]
    urgency_level: str  # Low, Medium, High
