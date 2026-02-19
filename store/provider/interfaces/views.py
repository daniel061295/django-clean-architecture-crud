from rest_framework import viewsets, status
from rest_framework.response import Response
from injector import inject
from uuid import UUID
from store.provider.application.use_cases.create_provider import CreateProvider
from store.provider.application.use_cases.list_providers import ListProviders
from store.provider.application.use_cases.get_provider import GetProvider
from store.provider.application.use_cases.update_provider import UpdateProvider
from store.provider.application.use_cases.delete_provider import DeleteProvider
from store.provider.interfaces.serializers import (
    CreateProviderSerializer, 
    UpdateProviderSerializer,
    ProviderResponseSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter

class ProviderView(viewsets.ViewSet):
    """
    ViewSet for managing Providers.
    """

    @inject
    def __init__(self, 
                 create_use_case: CreateProvider = None,
                 list_use_case: ListProviders = None,
                 get_use_case: GetProvider = None,
                 update_use_case: UpdateProvider = None,
                 delete_use_case: DeleteProvider = None,
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
        responses={200: ProviderResponseSerializer(many=True)}
    )
    def list(self, request):
        """List all providers with pagination and filtering."""
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        filters = {
            "name": request.query_params.get("name"),
            "active": request.query_params.get("active")
        }
        if filters["active"] is not None:
             filters["active"] = filters["active"].lower() == 'true'

        result, total_count = self.list_use_case.execute(page, page_size, filters)
        serializer = ProviderResponseSerializer(result, many=True)
        return Response({
            "data": serializer.data,
            "total": total_count,
            "page": page,
            "page_size": page_size
        })

    @extend_schema(request=CreateProviderSerializer, responses={201: ProviderResponseSerializer})
    def create(self, request):
        """Creates a new Provider."""
        serializer = CreateProviderSerializer(data=request.data)
        if serializer.is_valid():
            try:
                dto = serializer.to_dto()
                result = self.create_use_case.execute(dto)
                response_serializer = ProviderResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={200: ProviderResponseSerializer},
        parameters=[OpenApiParameter("id", UUID, location=OpenApiParameter.PATH)]
    )
    def retrieve(self, request, pk=None):
        """Retrieve a provider by ID."""
        try:
            provider_id = UUID(pk)
        except ValueError:
             return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)

        result = self.get_use_case.execute(provider_id)
        if not result:
            return Response({"error": "Provider not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = ProviderResponseSerializer(result)
        return Response(serializer.data)

    @extend_schema(
        request=UpdateProviderSerializer, 
        responses={200: ProviderResponseSerializer},
        parameters=[OpenApiParameter("id", UUID, location=OpenApiParameter.PATH)]
    )
    def update(self, request, pk=None):
        """Update a provider."""
        try:
            provider_id = UUID(pk)
        except ValueError:
             return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UpdateProviderSerializer(data=request.data)
        if serializer.is_valid():
            try:
                dto = serializer.to_dto(provider_id)
                result = self.update_use_case.execute(dto)
                response_serializer = ProviderResponseSerializer(result)
                return Response(response_serializer.data)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        responses={204: None},
        parameters=[OpenApiParameter("id", UUID, location=OpenApiParameter.PATH)]
    )
    def destroy(self, request, pk=None):
        """Delete a provider."""
        try:
            provider_id = UUID(pk)
        except ValueError:
             return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            self.delete_use_case.execute(provider_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
