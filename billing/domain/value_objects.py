"""
Billing Domain Value Objects — Pure Python enumerations and immutable objects.
"""
from enum import Enum


class SubscriptionStatus(str, Enum):
    """
    Represents the lifecycle status of a user's subscription.

    Values are intentionally stored as strings for easy DB serialization.
    """

    ACTIVE = "ACTIVE"
    CANCELED = "CANCELED"
    PAST_DUE = "PAST_DUE"
    TRIALING = "TRIALING"
