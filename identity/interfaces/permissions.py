"""
Identity DRF Permission Classes — RBAC permission enforcement for API endpoints.

These classes integrate with Django Rest Framework's permission system
to enforce RBAC permissions based on user roles.

Usage:
    from identity.interfaces.permissions import HasPermission

    class MyView(APIView):
        permission_classes = [HasPermission]

        def get_permission_code(self) -> str:
            return "manage_users"
"""
from typing import Any, List, Optional
from uuid import UUID

from rest_framework.permissions import BasePermission
from rest_framework.request import Request

from identity.application.dtos import CheckUserPermissionInputDTO
from identity.application.use_cases import CheckUserPermission


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

    def __init__(self, check_permission: CheckUserPermission = None, **kwargs: Any):
        """
        Initialize the permission with injected use case.

        Args:
            check_permission: Use case for checking user permissions (injected manually)
            **kwargs: Additional keyword arguments
        """
        self.check_permission = check_permission
        super().__init__(**kwargs)

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

        # If no specific permission code is required, allow access
        # (rely on IsAuthenticated permission class for basic auth check)
        if not permission_code:
            return True

        # Lazy injection: get CheckUserPermission from Django injector if not provided
        if self.check_permission is None:
            try:
                from django_injector import get_injector
                injector = get_injector()
                self.check_permission = injector.get(CheckUserPermission)
            except (ImportError, Exception):
                # Fallback: create use case directly if injector not available
                from identity.infrastructure.repositories import DjangoUserRepository
                self.check_permission = CheckUserPermission(DjangoUserRepository())

        user_id: UUID = request.user.id
        input_dto = CheckUserPermissionInputDTO(
            user_id=user_id,
            permission_code=permission_code,
        )
        result = self.check_permission.execute(input_dto)
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

    def __init__(self, check_permission: CheckUserPermission = None, **kwargs: Any):
        """
        Initialize the permission with injected use case.

        Args:
            check_permission: Use case for checking user permissions (injected manually)
            **kwargs: Additional keyword arguments
        """
        self.check_permission = check_permission
        super().__init__(**kwargs)

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

        # Lazy injection: get CheckUserPermission from Django injector if not provided
        if self.check_permission is None:
            try:
                from django_injector import get_injector
                injector = get_injector()
                self.check_permission = injector.get(CheckUserPermission)
            except (ImportError, Exception):
                # Fallback: create use case directly if injector not available
                from identity.infrastructure.repositories import DjangoUserRepository
                self.check_permission = CheckUserPermission(DjangoUserRepository())

        user_id: UUID = request.user.id
        for code in permission_codes:
            input_dto = CheckUserPermissionInputDTO(
                user_id=user_id,
                permission_code=code,
            )
            result = self.check_permission.execute(input_dto)
            if result.has_permission:
                return True
        return False


class IsAuthenticated(BasePermission):
    """
    DRF Permission class that simply checks if the user is authenticated.

    This is a simpler alternative to DRF's built-in IsAuthenticated
    that works with the custom user model.
    """

    def has_permission(self, request: Request, view: Any) -> bool:
        """
        Check if the requesting user is authenticated.

        Args:
            request: The HTTP request being processed.
            view: The view handling the request.

        Returns:
            bool: True if the user is authenticated, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated)
