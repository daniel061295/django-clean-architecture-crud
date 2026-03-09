"""
Billing Application DTOs — Input and Output transfer objects for billing use cases.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID


# --- Authorization DTOs ---

@dataclass
class CheckSubscriptionStatusInputDTO:
    """Input DTO for checking subscription status."""
    user_id: UUID


@dataclass
class CheckSubscriptionStatusOutputDTO:
    """Output DTO for subscription status check result."""
    has_active_subscription: bool
    plan_id: Optional[str] = None
    plan_name: Optional[str] = None
    status: Optional[str] = None


@dataclass
class CheckDailyScanLimitInputDTO:
    """Input DTO for checking daily scan limit."""
    user_id: UUID
    plan_id: UUID


@dataclass
class CheckDailyScanLimitOutputDTO:
    """Output DTO for daily scan limit check result."""
    can_scan: bool
    scans_today: int = 0
    scan_limit: Optional[int] = None


@dataclass
class AuthorizePlantScanOutputDTO:
    """Output DTO for plant scan authorization result."""
    authorized: bool
    reason: Optional[str] = None  # e.g., "no_subscription", "scan_limit_exceeded"
    plan_name: Optional[str] = None
    scans_today: int = 0
    scan_limit: Optional[int] = None


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


# --- Create Subscription DTOs ---

@dataclass
class CreateSubscriptionInputDTO:
    """Input DTO for creating a subscription."""
    user_id: UUID
    plan_id: UUID
    start_date: datetime
    end_date: Optional[datetime] = None


@dataclass
class CreateFreeSubscriptionForUserInputDTO:
    """Input DTO for creating FREE subscription automatically for new users."""
    user_id: UUID

@dataclass
class CreatePaymentIntentInputDTO:
    user_id: UUID
    plan_id: UUID

@dataclass
class CreatePaymentIntentOutputDTO:
    client_secret: str
    amount: float
    currency: str

@dataclass
class HandleStripeWebhookInputDTO:
    payload: bytes
    sig_header: str

