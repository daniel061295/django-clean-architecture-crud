from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from uuid import UUID

from store.infrastructure.repositories import DjangoPlantItemRepository
from store.application.use_cases.create_plant_item import CreatePlantItem
from store.application.use_cases.list_plant_items import ListPlantItems
from store.application.use_cases.get_plant_item import GetPlantItem
from store.application.use_cases.update_plant_item import UpdatePlantItem
from store.application.use_cases.delete_plant_item import DeletePlantItem
from store.application.dtos import ListPlantItemsQueryDTO
from store.domain.exceptions import DomainError, PlantItemNotFoundError
from store.interfaces.serializers import (
    CreatePlantItemSerializer, 
    UpdatePlantItemSerializer, 
    PlantItemResponseSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

class PlantItemView(APIView):
    def get_repository(self):
        return DjangoPlantItemRepository()

    @extend_schema(
        request=CreatePlantItemSerializer,
        responses={201: PlantItemResponseSerializer}
    )
    def post(self, request):
        serializer = CreatePlantItemSerializer(data=request.data)
        if serializer.is_valid():
            dto = serializer.to_dto()
            use_case = CreatePlantItem(self.get_repository())
            result = use_case.execute(dto)
            response_serializer = PlantItemResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='page_size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='min_price', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='max_price', type=OpenApiTypes.FLOAT, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='is_available', type=OpenApiTypes.BOOL, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='name_contains', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY),
        ],
        responses=PlantItemResponseSerializer(many=True)
    )
    def get(self, request):
        query_dto = ListPlantItemsQueryDTO(
            page=int(request.query_params.get('page', 1)),
            page_size=int(request.query_params.get('page_size', 10)),
            min_price=float(request.query_params.get('min_price')) if request.query_params.get('min_price') else None,
            max_price=float(request.query_params.get('max_price')) if request.query_params.get('max_price') else None,
            is_available=bool(request.query_params.get('is_available')) if request.query_params.get('is_available') is not None else None,
            name_contains=request.query_params.get('name_contains')
        )
        
        use_case = ListPlantItems(self.get_repository())
        result = use_case.execute(query_dto)
        
        response_serializer = PlantItemResponseSerializer(result.items, many=True)
        return Response({
            'items': response_serializer.data,
            'page': result.page,
            'page_size': result.page_size,
            'total_count': result.total_count,
            'total_pages': result.total_pages
        })

class PlantItemDetailView(APIView):
    def get_repository(self):
        return DjangoPlantItemRepository()

    @extend_schema(
        responses=PlantItemResponseSerializer
    )
    def get(self, request, item_id):
        use_case = GetPlantItem(self.get_repository())
        result = use_case.execute(item_id)
        response_serializer = PlantItemResponseSerializer(result)
        return Response(response_serializer.data)

    @extend_schema(
        request=UpdatePlantItemSerializer,
        responses=PlantItemResponseSerializer
    )
    def put(self, request, item_id):
        serializer = UpdatePlantItemSerializer(data=request.data)
        if serializer.is_valid():
            dto = serializer.to_dto()
            use_case = UpdatePlantItem(self.get_repository())
            result = use_case.execute(item_id, dto)
            response_serializer = PlantItemResponseSerializer(result)
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: None}
    )
    def delete(self, request, item_id):
        use_case = DeletePlantItem(self.get_repository())
        use_case.execute(item_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
