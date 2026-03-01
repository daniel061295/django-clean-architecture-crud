"""
Billing Domain Repository Interfaces (Ports) — Pure Python ABCs.
"""
from abc import ABC, abstractmethod
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from billing.domain.entities import DailyUsage, Plan, Subscription


class PlanRepository(ABC):
    """Abstract interface for Plan data access."""

    @abstractmethod
    def save(self, plan: Plan) -> Plan:
        """Saves a plan and returns the persisted instance."""

    @abstractmethod
    def get_by_id(self, plan_id: UUID) -> Optional[Plan]:
        """Retrieves a plan by UUID. Returns None if not found."""

    @abstractmethod
    def list_active(self) -> List[Plan]:
        """Returns all plans where is_active=True."""

    @abstractmethod
    def list_all(self) -> List[Plan]:
        """Returns all plans regardless of status."""


class SubscriptionRepository(ABC):
    """Abstract interface for Subscription data access."""

    @abstractmethod
    def save(self, subscription: Subscription) -> Subscription:
        """Saves or updates a subscription record."""

    @abstractmethod
    def get_by_id(self, subscription_id: UUID) -> Optional[Subscription]:
        """Retrieves a subscription by UUID."""

    @abstractmethod
    def get_active_by_user(self, user_id: UUID) -> Optional[Subscription]:
        """Returns the current active subscription for the user, or None."""

    @abstractmethod
    def cancel_active_by_user(self, user_id: UUID) -> None:
        """Sets all active/trialing subscriptions for a user to CANCELED."""

    @abstractmethod
    def create(
        self,
        user_id: UUID,
        plan_id: UUID,
        start_date: datetime,
        end_date: Optional[datetime] = None,
    ) -> Subscription:
        """Creates a new subscription for a user."""


class DailyUsageRepository(ABC):
    """Abstract interface for DailyUsage data access."""

    @abstractmethod
    def save(self, usage: DailyUsage) -> DailyUsage:
        """Saves the daily usage record and returns the updated instance."""

    @abstractmethod
    def get_or_create(self, user_id: UUID, usage_date: date) -> DailyUsage:
        """
        Returns the DailyUsage record for a given user and date.

        Creates a fresh record with zero counts if one doesn't exist yet.
        This operation should be atomic to prevent race conditions.
        """

    @abstractmethod
    def get_today_usage(self, user_id: UUID) -> Optional[DailyUsage]:
        """
        Returns today's DailyUsage record for a user, or None if not found.
        """

