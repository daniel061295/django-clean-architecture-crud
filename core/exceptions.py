from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from store.plant_item.domain.exceptions import DomainError, PlantItemNotFoundError


class DynamoDBClientError(Exception):
    """
    Exception raised for basic errors during interactions with DynamoDB.
    """
    pass


def drf_exception_handler(exc, context):
    """
    Custom exception handler for Django Rest Framework.

    Maps domain-specific exceptions to appropriate HTTP responses:
    - PlantItemNotFoundError      → 404
    - ScanLimitExceededError      → 429 (Too Many Requests)
    - PermissionDeniedError       → 403 (Forbidden)
    - NoActiveSubscriptionError   → 402 (Payment Required)
    - DomainError (all others)    → 400 (Bad Request)

    Args:
        exc (Exception): The exception raised.
        context (dict): Context dictionary containing view info.

    Returns:
        Response: DRF Response object or None.
    """
    # Let DRF handle its own exceptions first (e.g. validation errors, auth errors)
    response = exception_handler(exc, context)

    if response is None:
        # Import lazily to avoid circular imports at module load time
        from billing.domain.exceptions import ScanLimitExceededError, NoActiveSubscriptionError  # noqa: PLC0415
        from identity.domain.exceptions import PermissionDeniedError, UserAlreadyExistsError  # noqa: PLC0415

        if isinstance(exc, UserAlreadyExistsError):
            return Response(
                {"error": str(exc), "code": "USER_ALREADY_EXISTS"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if isinstance(exc, ScanLimitExceededError):
            return Response(
                {"error": str(exc), "code": "SCAN_LIMIT_EXCEEDED"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        if isinstance(exc, PermissionDeniedError):
            return Response(
                {"error": str(exc), "code": "PERMISSION_DENIED"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if isinstance(exc, NoActiveSubscriptionError):
            return Response(
                {"error": str(exc), "code": "NO_ACTIVE_SUBSCRIPTION"},
                status=status.HTTP_402_PAYMENT_REQUIRED,
            )

        if isinstance(exc, PlantItemNotFoundError):
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exc, DomainError):
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return response
