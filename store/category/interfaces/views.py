from rest_framework import viewsets, status
from rest_framework.response import Response
from injector import inject
from uuid import UUID
from store.category.application.use_cases.create_category import CreateCategory
from store.category.application.use_cases.list_categories import ListCategories
from store.category.application.use_cases.get_category import GetCategory
from store.category.application.use_cases.update_category import UpdateCategory
from store.category.application.use_cases.delete_category import DeleteCategory
from store.category.interfaces.serializers import (
    CreateCategorySerializer, 
    UpdateCategorySerializer,
    CategoryResponseSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter

class CategoryView(viewsets.ViewSet):
    """
    ViewSet for managing Categories.
    """

    INVALID_UUID = "Invalid UUID"

    @inject
    def __init__(self, 
                 create_use_case: CreateCategory = None,
                 list_use_case: ListCategories = None,
                 get_use_case: GetCategory = None,
                 update_use_case: UpdateCategory = None,
                 delete_use_case: DeleteCategory = None,
                 **kwargs):
        self.create_use_case = create_use_case
        self.list_use_case = list_use_case
        self.get_use_case = get_use_case
        self.update_use_case = update_use_case
        self.delete_use_case = delete_use_case
        super().__init__(**kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="page", description="Page number", required=False, type=int),
            OpenApiParameter(name="page_size", description="Items per page", required=False, type=int),
            OpenApiParameter(name="name", description="Filter by name", required=False, type=str),
            OpenApiParameter(name="active", description="Filter by active status", required=False, type=bool),
        ],
        responses={200: CategoryResponseSerializer(many=True)}
    )
    def list(self, request):
        """List all categories with pagination and filtering."""
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        filters = {
            "name": request.query_params.get("name"),
            "active": request.query_params.get("active")
        }
        
        # Convert 'active' string to boolean if present
        if filters["active"] is not None:
             filters["active"] = filters["active"].lower() == 'true'

        result, total_count = self.list_use_case.execute(page, page_size, filters)
        serializer = CategoryResponseSerializer(result, many=True)
        return Response({
            "data": serializer.data,
            "total": total_count,
            "page": page,
            "page_size": page_size
        })

    @extend_schema(request=CreateCategorySerializer, responses={201: CategoryResponseSerializer})
    def create(self, request):
        """Creates a new Category."""
        serializer = CreateCategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                dto = serializer.to_dto()
                result = self.create_use_case.execute(dto)
                response_serializer = CategoryResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={200: CategoryResponseSerializer})
    def retrieve(self, request, pk=None):
        """Retrieve a category by ID."""
        try:
            category_id = UUID(pk)
        except ValueError:
             return Response({"error": self.INVALID_UUID}, status=status.HTTP_400_BAD_REQUEST)

        result = self.get_use_case.execute(category_id)
        if not result:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = CategoryResponseSerializer(result)
        return Response(serializer.data)

    @extend_schema(request=UpdateCategorySerializer, responses={200: CategoryResponseSerializer})
    def update(self, request, pk=None):
        """Update a category."""
        try:
            category_id = UUID(pk)
        except ValueError:
             return Response({"error": self.INVALID_UUID}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UpdateCategorySerializer(data=request.data)
        if serializer.is_valid():
            try:
                dto = serializer.to_dto(category_id)
                result = self.update_use_case.execute(dto)
                response_serializer = CategoryResponseSerializer(result)
                return Response(response_serializer.data)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={204: None})
    def destroy(self, request, pk=None):
        """Delete a category."""
        try:
            category_id = UUID(pk)
        except ValueError:
             return Response({"error": self.INVALID_UUID}, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.delete_use_case.execute(category_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
