from abc import ABC, abstractmethod
from typing import BinaryIO
from store.plant_health.domain.entities import PlantHealthReport

class PlantHealthService(ABC):
    """
    Domain Interface (Port) for Plant Health Analysis Service.
    """

    @abstractmethod
    def analyze_photo(self, photo: BinaryIO) -> PlantHealthReport:
        """
        Analyzes a plant photo to diagnose health and pests.

        Args:
            photo (BinaryIO): The image file to analyze.

        Returns:
            PlantHealthReport: The diagnosis report.
        """
        pass
