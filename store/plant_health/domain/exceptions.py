class PlantHealthAnalysisError(Exception):
    """Base exception for plant health analysis errors."""
    pass

class LowConfidenceError(PlantHealthAnalysisError):
    """Raised when the analysis confidence is too low after retries."""
    pass

class InvalidPlantImageError(PlantHealthAnalysisError):
    """Raised when the provided image does not contain a clear or recognizable plant."""
    pass
