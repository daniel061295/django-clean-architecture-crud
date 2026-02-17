class DomainError(Exception):
    """Base exception for domain errors."""


class InvalidStockError(DomainError):
    """Raised when stock is invalid (e.g. negative)."""


class InvalidPriceError(DomainError):
    """Raised when price is invalid (e.g. negative)."""


class PlantItemNotFoundError(DomainError):
    """Raised when a plant item is not found."""
