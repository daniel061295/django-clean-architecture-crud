from dataclasses import dataclass
from typing import List, BinaryIO
from uuid import UUID

@dataclass
class AnalyzePlantHealthInputDTO:
    """
    Data Transfer Object for the input of the AnalyzePlantHealth use case.

    Attributes:
        photo: The plant image file to analyze.
        user_id: UUID of the authenticated user performing the scan.
    """
    photo: BinaryIO
    user_id: UUID


@dataclass
class PlantHealthAnalysisResponseDTO:
    """
    Data Transfer Object for the output of the AnalyzePlantHealth use case.
    """
    is_healthy: bool
    title: str
    diagnosis: str
    confidence: float
    treatment: List[str]
    urgency_level: str
    photo: str

