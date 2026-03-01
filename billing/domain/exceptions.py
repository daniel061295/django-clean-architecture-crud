"""
Billing Domain Exceptions — Pure Python, no framework dependencies.
"""
from store.plant_item.domain.exceptions import DomainError


class ScanLimitExceededError(DomainError):
    """Raised when a user has reached their daily scan limit for their active plan."""


class NoActiveSubscriptionError(DomainError):
    """Raised when a user attempts a restricted action without an active subscription."""


class PlanNotFoundError(DomainError):
    """Raised when a plan cannot be found by the given identifier."""


class SubscriptionNotFoundError(DomainError):
    """Raised when a subscription cannot be found for the given user."""


class PlanAlreadyExistsError(DomainError):
    """Raised when attempting to create a plan with a name that already exists."""


class SubscriptionAlreadyExistsError(DomainError):
    """Raised when attempting to create a subscription for a user that already has one."""
