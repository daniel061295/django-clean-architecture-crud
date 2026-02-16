from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from injector import inject
from store.application.use_cases.create_plant_item import CreatePlantItem
from store.application.use_cases.list_plant_items import ListPlantItems
from store.application.use_cases.get_plant_item import GetPlantItem
from store.application.use_cases.update_plant_item import UpdatePlantItem
from store.application.use_cases.delete_plant_item import DeletePlantItem
from store.application.dtos import ListPlantItemsQueryDTO
from store.interfaces.serializers import (
    CreatePlantItemSerializer,
    UpdatePlantItemSerializer,
    PlantItemResponseSerializer,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from uuid import UUID


class PlantItemView(viewsets.ViewSet):
    """
    ViewSet for managing PlantItems.
    Handles listing, creating, retrieving, updating, and deleting plant items.
    """

    INVALID_UUID_MESSAGE = "Invalid UUID format"

    @inject
    def __init__(
        self,
        create_use_case: CreatePlantItem,
        list_use_case: ListPlantItems,
        get_use_case: GetPlantItem,
        update_use_case: UpdatePlantItem,
        delete_use_case: DeletePlantItem,
        **kwargs,
    ):
        self.create_use_case = create_use_case
        self.list_use_case = list_use_case
        self.get_use_case = get_use_case
        self.update_use_case = update_use_case
        self.delete_use_case = delete_use_case
        super().__init__(**kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="page", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(
                name="page_size", type=OpenApiTypes.INT, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="min_price", type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="max_price", type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="is_available", type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name="name_contains", type=OpenApiTypes.STR, location=OpenApiParameter.QUERY
            ),
        ],
        responses=PlantItemResponseSerializer(many=True),
    )
    def list(self, request):
        """
        Lists PlantItems with pagination and filtering.
        """
        # Handle query params manually converting to types as needed
        query_dto = ListPlantItemsQueryDTO(
            page=int(request.query_params.get("page", 1)),
            page_size=int(request.query_params.get("page_size", 10)),
            min_price=(
                float(request.query_params.get("min_price"))
                if request.query_params.get("min_price")
                else None
            ),
            max_price=(
                float(request.query_params.get("max_price"))
                if request.query_params.get("max_price")
                else None
            ),
            is_available=(
                bool(request.query_params.get("is_available"))
                if request.query_params.get("is_available") is not None
                else None
            ),
            name_contains=request.query_params.get("name_contains"),
        )

        result = self.list_use_case.execute(query_dto)

        response_serializer = PlantItemResponseSerializer(result.items, many=True)
        return Response(
            {
                "items": response_serializer.data,
                "page": result.page,
                "page_size": result.page_size,
                "total_count": result.total_count,
                "total_pages": result.total_pages,
            }
        )

    @extend_schema(request=CreatePlantItemSerializer, responses={201: PlantItemResponseSerializer})
    def create(self, request):
        """
        Creates a new PlantItem.
        """
        serializer = CreatePlantItemSerializer(data=request.data)
        if serializer.is_valid():
            dto = serializer.to_dto()
            result = self.create_use_case.execute(dto)
            response_serializer = PlantItemResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses=PlantItemResponseSerializer)
    def retrieve(self, request, pk=None):
        """
        Retrieves a PlantItem by ID.
        """
        try:
            item_id = UUID(pk)
        except ValueError:
            return Response(
                {"error": self.INVALID_UUID_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )

        result = self.get_use_case.execute(item_id)
        response_serializer = PlantItemResponseSerializer(result)
        return Response(response_serializer.data)

    @extend_schema(request=UpdatePlantItemSerializer, responses=PlantItemResponseSerializer)
    def update(self, request, pk=None):
        """
        Updates a PlantItem by ID.
        """
        try:
            item_id = UUID(pk)
        except ValueError:
            return Response(
                {"error": self.INVALID_UUID_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UpdatePlantItemSerializer(data=request.data)
        if serializer.is_valid():
            dto = serializer.to_dto()
            result = self.update_use_case.execute(item_id, dto)
            response_serializer = PlantItemResponseSerializer(result)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        """
        Deletes a PlantItem by ID.
        """
        try:
            item_id = UUID(pk)
        except ValueError:
            return Response(
                {"error": self.INVALID_UUID_MESSAGE}, status=status.HTTP_400_BAD_REQUEST
            )

        self.delete_use_case.execute(item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
