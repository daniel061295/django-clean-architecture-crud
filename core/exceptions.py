from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from store.plant_item.domain.exceptions import DomainError, PlantItemNotFoundError


def drf_exception_handler(exc, context):
    """
    Custom exception handler for Django Rest Framework.

    It handles domain-specific exceptions and converts them into appropriate
    HTTP responses.

    Args:
        exc (Exception): The exception raised.
        context (dict): Context dictionary containing view info.

    Returns:
        Response: DRF Response object or None.
    """
    response = exception_handler(exc, context)

    if response is None:
        if isinstance(exc, PlantItemNotFoundError):
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exc, DomainError):
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    return response
