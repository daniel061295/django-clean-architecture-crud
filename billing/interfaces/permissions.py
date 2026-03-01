"""
Billing DRF Permission Classes — Subscription-based permission enforcement for API endpoints.

These classes integrate with Django Rest Framework's permission system
to enforce subscription-based permissions (active subscription, scan limits, etc.).

Usage:
    from billing.interfaces.permissions import HasActiveSubscription

    class PlantHealthView(APIView):
        permission_classes = [HasActiveSubscription]
"""
from typing import Any, Optional
from uuid import UUID

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from billing.application.use_cases import AuthorizePlantScan, CheckSubscriptionStatus


class HasActiveSubscription(BasePermission):
    """
    DRF Permission class that checks if the user has an active subscription.

    This permission requires the user to be authenticated and verifies that
    the user has an active subscription in the billing system.

    Usage:
        class PremiumFeatureView(APIView):
            permission_classes = [HasActiveSubscription]
    """

    def __init__(
        self,
        check_subscription: CheckSubscriptionStatus = None,
        **kwargs: Any,
    ):
        """
        Initialize the permission with injected use case.

        Args:
            check_subscription: Use case for checking subscription status (injected manually)
            **kwargs: Additional keyword arguments
        """
        self.check_subscription = check_subscription
        super().__init__(**kwargs)

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if the requesting user has an active subscription.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            bool: True if the user has an active subscription, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Lazy injection: get CheckSubscriptionStatus from Django injector if not provided
        if self.check_subscription is None:
            try:
                from django_injector import get_injector
                injector = get_injector()
                self.check_subscription = injector.get(CheckSubscriptionStatus)
            except (ImportError, Exception):
                # Fallback: create use case directly if injector not available
                from billing.infrastructure.repositories import DjangoSubscriptionRepository, DjangoPlanRepository
                self.check_subscription = CheckSubscriptionStatus(
                    DjangoSubscriptionRepository(),
                    DjangoPlanRepository()
                )

        user_id: UUID = request.user.id
        from billing.application.dtos import CheckSubscriptionStatusInputDTO  # noqa: PLC0415

        input_dto = CheckSubscriptionStatusInputDTO(user_id=user_id)
        result = self.check_subscription.execute(input_dto)
        return result.has_active_subscription


class HasSubscriptionScanPermission(BasePermission):
    """
    DRF Permission class for plant scanning endpoints.

    This permission verifies:
    1. User is authenticated
    2. User has an active subscription
    3. User has not exceeded their daily scan limit

    This combines subscription status validation with daily scan limit checking.

    Usage:
        class PlantHealthView(APIView):
            permission_classes = [HasSubscriptionScanPermission]
    """

    def __init__(self, authorize_scan: AuthorizePlantScan = None, **kwargs: Any):
        """
        Initialize the permission with injected use case.

        Args:
            authorize_scan: Use case for authorizing plant scans (injected manually)
            **kwargs: Additional keyword arguments
        """
        self.authorize_scan = authorize_scan
        super().__init__(**kwargs)

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if the user can perform a plant scan.

        Verifies authentication, active subscription, and daily scan limit.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            bool: True if the user can scan, False otherwise.
            
        Raises:
            NoActiveSubscriptionError: If user doesn't have active subscription.
            ScanLimitExceededError: If user exceeded daily scan limit.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Lazy injection: get AuthorizePlantScan from Django injector if not provided
        if self.authorize_scan is None:
            try:
                from django_injector import get_injector
                injector = get_injector()
                self.authorize_scan = injector.get(AuthorizePlantScan)
            except (ImportError, Exception):
                # Fallback: create use case directly if injector not available
                from billing.infrastructure.repositories import (
                    DjangoSubscriptionRepository,
                    DjangoPlanRepository,
                    DjangoDailyUsageRepository,
                )
                self.authorize_scan = AuthorizePlantScan(
                    DjangoSubscriptionRepository(),
                    DjangoPlanRepository(),
                    DjangoDailyUsageRepository(),
                )

        user_id: UUID = request.user.id
        result = self.authorize_scan.execute(user_id)
        
        # If not authorized, raise appropriate exception based on reason
        if not result.authorized:
            if result.reason == "scan_limit_exceeded":
                from billing.domain.exceptions import ScanLimitExceededError
                raise ScanLimitExceededError(
                    f"Daily scan limit of {result.scan_limit} reached. "
                    f"You have performed {result.scans_today} scans today. "
                    "Please upgrade your plan or try again tomorrow."
                )
            elif result.reason == "no_subscription":
                from billing.domain.exceptions import NoActiveSubscriptionError
                raise NoActiveSubscriptionError(
                    "No active subscription found. Please subscribe to a plan."
                )
            return False
        
        return True

    def has_permission_details(
        self, request: Request, view: Any
    ) -> dict[str, Any]:
        """
        Get detailed information about why permission was granted or denied.

        This method can be used in views to provide feedback to the user.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            dict: Details about the authorization result.
        """
        if not request.user or not request.user.is_authenticated:
            return {"authorized": False, "reason": "not_authenticated"}

        if self.authorize_scan is None:
            return {"authorized": False, "reason": "service_unavailable"}

        user_id: UUID = request.user.id
        result = self.authorize_scan.execute(user_id)

        return {
            "authorized": result.authorized,
            "reason": result.reason,
            "plan_name": result.plan_name,
            "scans_today": result.scans_today,
            "scan_limit": result.scan_limit,
        }


class CanPerformScanOperation(BasePermission):
    """
    Alternative permission class that provides more granular control.

    This permission is similar to HasSubscriptionScanPermission but allows
    views to access authorization details through the view instance.

    Usage:
        class PlantHealthView(APIView):
            permission_classes = [CanPerformScanOperation]

            def post(self, request):
                # Access authorization details
                permission = self.get_permissions()[0]
                details = permission.get_authorization_details(request)
                ...
    """

    def __init__(self, authorize_scan: AuthorizePlantScan = None, **kwargs: Any):
        """
        Initialize the permission with injected use case.

        Args:
            authorize_scan: Use case for authorizing plant scans (injected manually)
            **kwargs: Additional keyword arguments
        """
        self.authorize_scan = authorize_scan
        self._last_result: Optional[Any] = None
        super().__init__(**kwargs)

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if the user can perform a plant scan.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            bool: True if the user can scan, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Lazy injection: get AuthorizePlantScan from Django injector if not provided
        if self.authorize_scan is None:
            try:
                from django_injector import get_injector
                injector = get_injector()
                self.authorize_scan = injector.get(AuthorizePlantScan)
            except (ImportError, Exception):
                # Fallback: create use case directly if injector not available
                from billing.infrastructure.repositories import (
                    DjangoSubscriptionRepository,
                    DjangoPlanRepository,
                    DjangoDailyUsageRepository,
                )
                self.authorize_scan = AuthorizePlantScan(
                    DjangoSubscriptionRepository(),
                    DjangoPlanRepository(),
                    DjangoDailyUsageRepository(),
                )

        user_id: UUID = request.user.id
        result = self.authorize_scan.execute(user_id)
        self._last_result = result
        return result.authorized

    def get_authorization_details(self, request: Request) -> dict[str, Any]:
        """
        Get the authorization details from the last permission check.

        Args:
            request: The HTTP request being processed.

        Returns:
            dict: Authorization details including reason, plan, and usage.
        """
        if self._last_result is None:
            # Run the check if not already done
            self.has_permission(request, None)

        if self._last_result is None:
            return {"authorized": False, "reason": "unknown"}

        return {
            "authorized": self._last_result.authorized,
            "reason": self._last_result.reason,
            "plan_name": self._last_result.plan_name,
            "scans_today": self._last_result.scans_today,
            "scan_limit": self._last_result.scan_limit,
        }
