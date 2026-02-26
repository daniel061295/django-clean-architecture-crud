"""
Billing Application DTOs — Input and Output transfer objects for billing use cases.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import UUID


# --- Plan DTOs ---

@dataclass
class CreatePlanInputDTO:
    """Input DTO for the CreatePlan use case."""
    name: str
    price: float
    scan_limit_per_day: Optional[int] = None
    ads_enabled: bool = True
    features: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanOutputDTO:
    """Output DTO representing a SaaS plan."""
    id: str
    name: str
    price: float
    scan_limit_per_day: Optional[int]
    ads_enabled: bool
    features: Dict[str, Any]
    is_active: bool


# --- Subscription DTOs ---

@dataclass
class ChangePlanInputDTO:
    """Input DTO for the ChangePlan use case."""
    user_id: UUID
    plan_id: UUID


@dataclass
class CancelSubscriptionInputDTO:
    """Input DTO for the CancelSubscription use case."""
    user_id: UUID


@dataclass
class SubscriptionOutputDTO:
    """Output DTO representing a subscription."""
    id: str
    user_id: str
    plan_id: str
    status: str
    start_date: str
    end_date: Optional[str]
    external_id: Optional[str]


# --- My Subscription (composite response) ---

@dataclass
class MySubscriptionOutputDTO:
    """
    Composite DTO for the GET /billing/me endpoint.
    Combines plan, subscription status, and today's usage.
    """
    plan_name: str
    plan_id: str
    status: str
    scan_limit_per_day: Optional[int]
    ads_enabled: bool
    usage_today: int
    features: Dict[str, Any] = field(default_factory=dict)
