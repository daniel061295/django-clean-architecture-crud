"""
Core DRF Permission Classes — Permission enforcement for API endpoints.

These classes integrate with Django Rest Framework's permission system
to enforce RBAC permissions based on user roles.

Usage:
    class MyView(APIView):
        permission_classes = [HasPermission]

        def get_permission_code(self) -> str:
            return "manage_users"
"""
from datetime import date
from typing import Any, List, Optional
from uuid import UUID

from django.apps import apps
from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from billing.domain.interfaces import DailyUsageRepository, PlanRepository, SubscriptionRepository
from billing.domain.value_objects import SubscriptionStatus
from identity.application.dtos import CheckUserPermissionInputDTO
from identity.application.use_cases import CheckUserPermission


def _get_injector() -> Optional[Any]:
    """
    Get the Django Injector instance from the django_injector app config.

    Returns:
        The injector instance, or None if not available.
    """
    try:
        injector_app = apps.get_app_config("django_injector")
        return getattr(injector_app, "injector", None)
    except LookupError:
        return None


class HasPermission(BasePermission):
    """
    DRF Permission class that checks if the user has a specific permission code.

    This permission requires the user to be authenticated and verifies that
    the user has been granted the specified permission through their roles.

    Usage:
        class MyView(APIView):
            permission_classes = [HasPermission]

            def get_permission_code(self) -> str:
                return "manage_users"
    """

    def get_permission_code(self) -> str:
        """
        Override this method in the view to specify the required permission code.

        Returns:
            str: The permission code required to access the endpoint.
        """
        return ""

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if the requesting user has the required permission.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            bool: True if the user has the permission, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get permission code from view
        permission_code = getattr(view, "get_permission_code", lambda: "")()
        if not permission_code:
            return False

        # Get use case from injector
        injector = _get_injector()
        if injector is None:
            return False

        try:
            check_permission = injector.get(CheckUserPermission)
        except Exception:  # noqa: BLE001
            return False

        user_id: UUID = request.user.id
        input_dto = CheckUserPermissionInputDTO(
            user_id=user_id,
            permission_code=permission_code,
        )
        result = check_permission.execute(input_dto)
        return result.has_permission


class HasAnyPermission(BasePermission):
    """
    DRF Permission class that checks if the user has at least one of several permissions.

    This permission requires the user to be authenticated and verifies that
    the user has been granted at least one of the specified permissions through their roles.

    Usage:
        class MyView(APIView):
            permission_classes = [HasAnyPermission]

            def get_permission_codes(self) -> List[str]:
                return ["manage_users", "admin_access"]
    """

    def get_permission_codes(self) -> List[str]:
        """
        Override this method in the view to specify the required permission codes.

        Returns:
            List[str]: List of permission codes, any of which grants access.
        """
        return []

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if the requesting user has at least one of the required permissions.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            bool: True if the user has at least one permission, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get permission codes from view
        permission_codes = getattr(view, "get_permission_codes", lambda: [])()
        if not permission_codes:
            return False

        # Get use case from injector
        injector = _get_injector()
        if injector is None:
            return False

        try:
            check_permission = injector.get(CheckUserPermission)
        except Exception:  # noqa: BLE001
            return False

        user_id: UUID = request.user.id
        for code in permission_codes:
            input_dto = CheckUserPermissionInputDTO(
                user_id=user_id,
                permission_code=code,
            )
            result = check_permission.execute(input_dto)
            if result.has_permission:
                return True
        return False


class HasSubscriptionScanPermission(BasePermission):
    """
    DRF Permission class for plant scanning endpoints.

    This permission verifies:
    1. User is authenticated
    2. User has the 'scan_plant' permission
    3. User has an active subscription
    4. User has not exceeded their daily scan limit

    This combines RBAC permission checking with subscription status validation.

    Usage:
        class PlantHealthView(APIView):
            permission_classes = [HasSubscriptionScanPermission]
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if the user can perform a plant scan.

        Verifies authentication, scan_plant permission, active subscription,
        and daily scan limit.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            bool: True if the user can scan, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        # Get use cases and repositories from injector
        injector = _get_injector()
        if injector is None:
            return False

        try:
            check_permission = injector.get(CheckUserPermission)
            subscription_repository = injector.get(SubscriptionRepository)
            daily_usage_repository = injector.get(DailyUsageRepository)
            plan_repository = injector.get(PlanRepository)
        except Exception:  # noqa: BLE001
            return False

        user_id: UUID = request.user.id

        # Check scan_plant permission
        input_dto = CheckUserPermissionInputDTO(
            user_id=user_id,
            permission_code="scan_plant",
        )
        result = check_permission.execute(input_dto)
        if not result.has_permission:
            return False

        # Check active subscription
        subscription = subscription_repository.get_active_by_user(user_id)
        if subscription is None:
            return False

        if subscription.status != SubscriptionStatus.ACTIVE:
            return False

        # Get plan and check scan limit
        plan = plan_repository.get_by_id(subscription.plan_id)
        if plan is None:
            return False

        # Check if user has reached daily limit
        daily_usage = daily_usage_repository.get_today_usage(user_id)
        if daily_usage is not None and plan.scan_limit_per_day is not None:
            if daily_usage.scans_count >= plan.scan_limit_per_day:
                return False

        return True
