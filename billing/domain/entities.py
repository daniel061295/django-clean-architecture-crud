"""
Billing Domain Entities — Pure Python, no framework dependencies.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, Optional
from uuid import UUID

from billing.domain.value_objects import SubscriptionStatus


@dataclass
class Plan:
    """
    Domain Entity representing a SaaS pricing plan.

    Attributes:
        id: Unique identifier.
        name: Public display name (e.g. 'FREE', 'PRO').
        price: Monthly price in the app's currency unit.
        scan_limit_per_day: Max scans allowed per day. None means unlimited.
        ads_enabled: Whether ads are shown to users on this plan.
        features: Arbitrary dict of feature flags for this plan.
        is_active: Whether this plan is publicly available.
    """

    id: UUID
    name: str
    price: float
    scan_limit_per_day: Optional[int]
    ads_enabled: bool
    features: Dict[str, Any]
    is_active: bool = True

    def is_unlimited(self) -> bool:
        """Returns True if this plan has no daily scan limit."""
        return self.scan_limit_per_day is None

    @classmethod
    def create(
        cls,
        name: str,
        price: float,
        scan_limit_per_day: Optional[int] = None,
        ads_enabled: bool = True,
        features: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
    ) -> "Plan":
        """Factory method to create a new Plan with a generated UUID."""
        return cls(
            id=uuid.uuid4(),
            name=name,
            price=price,
            scan_limit_per_day=scan_limit_per_day,
            ads_enabled=ads_enabled,
            features=features or {},
            is_active=is_active,
        )


@dataclass
class Subscription:
    """
    Domain Entity representing a user's active subscription to a plan.

    Attributes:
        id: Unique identifier.
        user_id: UUID of the subscribed user.
        plan_id: UUID of the plan.
        status: Current lifecycle status.
        start_date: When the subscription became active.
        end_date: When the subscription expires (None = ongoing).
        external_id: Optional ID from an external payment provider (e.g. Stripe).
    """

    id: UUID
    user_id: UUID
    plan_id: UUID
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime]
    external_id: Optional[str] = None

    def is_active(self) -> bool:
        """
        Returns True if the subscription is currently in an active state.

        A subscription is active when its status is ACTIVE or TRIALING,
        AND it has not passed its end_date (if one is set).
        """
        if self.status not in (SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING):
            return False
        if self.end_date is not None and datetime.utcnow() > self.end_date:
            return False
        return True

    @classmethod
    def create(
        cls,
        user_id: UUID,
        plan_id: UUID,
        status: SubscriptionStatus = SubscriptionStatus.ACTIVE,
        end_date: Optional[datetime] = None,
        external_id: Optional[str] = None,
    ) -> "Subscription":
        """Factory method to create a new Subscription with current timestamp."""
        return cls(
            id=uuid.uuid4(),
            user_id=user_id,
            plan_id=plan_id,
            status=status,
            start_date=datetime.utcnow(),
            end_date=end_date,
            external_id=external_id,
        )


@dataclass
class DailyUsage:
    """
    Domain Entity tracking how many scans a user has performed on a given day.

    Attributes:
        id: Unique identifier.
        user_id: UUID of the user.
        date: The calendar date this record covers.
        scans_count: Total scans performed this day.
        ads_watched: Total ads watched this day.
    """

    id: UUID
    user_id: UUID
    date: date
    scans_count: int = 0
    ads_watched: int = 0

    def increment_scan(self) -> None:
        """
        Increments the scan counter by one.

        This mutates state — the caller is responsible for persisting.
        """
        self.scans_count += 1

    def has_reached_limit(self, limit: Optional[int]) -> bool:
        """
        Returns True if the daily scan limit has been reached.

        Args:
            limit: Maximum allowed scans. None means unlimited.

        Returns:
            bool: True if scans_count >= limit and limit is not None.
        """
        if limit is None:
            return False
        return self.scans_count >= limit

    @classmethod
    def create(cls, user_id: UUID, usage_date: date) -> "DailyUsage":
        """Factory method to create a fresh DailyUsage record for a given user and date."""
        return cls(id=uuid.uuid4(), user_id=user_id, date=usage_date)
