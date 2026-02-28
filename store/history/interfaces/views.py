"""
History Interface Views — DRF ViewSet for History management.

Follows the same @inject pattern as PlantItemView / TipView.
All logic is delegated to use cases via constructor injection.
"""
from dataclasses import asdict
from uuid import UUID

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from injector import inject
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from store.history.application.dtos import (
    CreateHistoryInputDTO,
    GetHistoryInputDTO,
    GetHistoryByUserInputDTO,
)
from store.history.application.use_cases import (
    CreateHistoryUseCase,
    GetHistoryUseCase,
    GetAllHistoryUseCase,
    GetHistoryByUserUseCase,
    DeleteHistoryUseCase,
    DeleteAllHistoryUseCase,
)
from store.history.interfaces.serializers import CreateHistoryInputSerializer


class HistoryView(viewsets.ViewSet):
    """
    ViewSet for managing plant health diagnosis History records.
    Handles list, create, retrieve, destroy, destroy_all, and by_user actions.
    """

    INVALID_UUID_MESSAGE = "Invalid UUID format"

    @inject
    def __init__(
        self,
        create_use_case: CreateHistoryUseCase = None,
        get_all_use_case: GetAllHistoryUseCase = None,
        get_use_case: GetHistoryUseCase = None,
        get_by_user_use_case: GetHistoryByUserUseCase = None,
        delete_use_case: DeleteHistoryUseCase = None,
        delete_all_use_case: DeleteAllHistoryUseCase = None,
        **kwargs,
    ):
        self.create_use_case = create_use_case
        self.get_all_use_case = get_all_use_case
        self.get_use_case = get_use_case
        self.get_by_user_use_case = get_by_user_use_case
        self.delete_use_case = delete_use_case
        self.delete_all_use_case = delete_all_use_case
        super().__init__(**kwargs)

    @extend_schema(
        responses={200: OpenApiResponse(description="List of all history records")},
        description="Retrieves a list of all diagnosis history records.",
    )
    def list(self, request: Request) -> Response:
        """Returns all history records."""
        output_dtos = self.get_all_use_case.execute()
        return Response([asdict(dto) for dto in output_dtos], status=status.HTTP_200_OK)

    @extend_schema(
        request=CreateHistoryInputSerializer,
        responses={201: OpenApiResponse(description="History record created")},
        description="Creates a new AI diagnosis history record.",
    )
    def create(self, request: Request) -> Response:
        """Creates a new history record."""
        serializer = CreateHistoryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreateHistoryInputDTO(**serializer.validated_data)
        output_dto = self.create_use_case.execute(input_dto)
        return Response(asdict(output_dto), status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={
            200: OpenApiResponse(description="A single history record"),
            404: OpenApiResponse(description="History not found"),
        },
        parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)],
        description="Retrieves a history record by its UUID.",
    )
    def retrieve(self, request: Request, pk: str = None) -> Response:
        """Returns a single history record by UUID."""
        try:
            history_id = UUID(pk)
        except (ValueError, AttributeError):
            return Response(
                {"error": self.INVALID_UUID_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            input_dto = GetHistoryInputDTO(id=str(history_id))
            output_dto = self.get_use_case.execute(input_dto)
            return Response(asdict(output_dto), status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="History deleted successfully"),
            404: OpenApiResponse(description="History not found"),
        },
        parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)],
        description="Deletes a history record by its UUID.",
    )
    def destroy(self, request: Request, pk: str = None) -> Response:
        """Deletes a single history record by UUID."""
        try:
            history_id = UUID(pk)
        except (ValueError, AttributeError):
            return Response(
                {"error": self.INVALID_UUID_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            input_dto = GetHistoryInputDTO(id=str(history_id))
            self.delete_use_case.execute(input_dto)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={204: OpenApiResponse(description="All history records deleted")},
        description="Deletes all history records.",
    )
    @action(detail=False, methods=["delete"], url_path="delete-all")
    def destroy_all(self, request: Request) -> Response:
        """Deletes all history records."""
        self.delete_all_use_case.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={200: OpenApiResponse(description="History records for the given user")},
        parameters=[OpenApiParameter("user_id", OpenApiTypes.STR, OpenApiParameter.PATH)],
        description="Retrieves all history records for a specific user.",
    )
    @action(detail=False, methods=["get"], url_path="by-user/(?P<user_id>[^/.]+)")
    def by_user(self, request: Request, user_id: str = None) -> Response:
        """Returns all history records for a specific user."""
        input_dto = GetHistoryByUserInputDTO(user_id=user_id)
        output_dtos = self.get_by_user_use_case.execute(input_dto)
        return Response([asdict(dto) for dto in output_dtos], status=status.HTTP_200_OK)
