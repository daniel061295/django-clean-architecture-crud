from dataclasses import dataclass
from typing import List, BinaryIO

@dataclass
class AnalyzePlantHealthInputDTO:
    """
    Data Transfer Object for the input of the AnalyzePlantHealth use case.
    """
    photo: BinaryIO


@dataclass
class PlantHealthAnalysisResponseDTO:
    """
    Data Transfer Object for the output of the AnalyzePlantHealth use case.
    """
    is_healthy: bool
    diagnosis: str
    confidence: float
    treatment: List[str]
    urgency_level: str
