import uuid
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from injector import inject

from store.tips.application.use_cases import (
    CreateTipUseCase, GetTipUseCase, GetAllTipsUseCase,
    UpdateTipUseCase, DeleteTipUseCase, GetRandomTipUseCase
)
from store.tips.application.dtos import CreateTipInputDTO, UpdateTipInputDTO
from store.tips.interfaces.serializers import (
    CreateTipInputSerializer, UpdateTipInputSerializer, TipOutputSerializer
)

@extend_schema_view(
    retrieve=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)]),
    update=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)]),
    destroy=extend_schema(parameters=[OpenApiParameter("id", OpenApiTypes.UUID, OpenApiParameter.PATH)])
)
class TipViewSet(viewsets.ViewSet):
    """
    ViewSet for Tip CRUD operations.
    """
    serializer_class = TipOutputSerializer
    @inject
    def __init__(
        self,
        create_use_case: CreateTipUseCase = None,
        get_use_case: GetTipUseCase = None,
        get_all_use_case: GetAllTipsUseCase = None,
        update_use_case: UpdateTipUseCase = None,
        delete_use_case: DeleteTipUseCase = None,
        get_random_use_case: GetRandomTipUseCase = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._create_use_case = create_use_case
        self._get_use_case = get_use_case
        self._get_all_use_case = get_all_use_case
        self._update_use_case = update_use_case
        self._delete_use_case = delete_use_case
        self._get_random_use_case = get_random_use_case

    @extend_schema(
        request=CreateTipInputSerializer,
        responses={201: TipOutputSerializer},
        summary="Create a new Tip"
    )
    def create(self, request):
        serializer = CreateTipInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        input_dto = CreateTipInputDTO(**serializer.validated_data)
        output_dto = self._create_use_case.execute(input_dto)
        
        return Response(output_dto.__dict__, status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={200: TipOutputSerializer, 404: OpenApiResponse(description="Not Found")},
        summary="Retrieve a random Tip"
    )
    @action(detail=False, methods=['get'])
    def random(self, request):
        try:
            output_dto = self._get_random_use_case.execute()
            return Response(output_dto.__dict__, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={200: TipOutputSerializer(many=True)},
        summary="List all Tips"
    )
    def list(self, request):
        output_dtos = self._get_all_use_case.execute()
        return Response([dto.__dict__ for dto in output_dtos], status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: TipOutputSerializer, 404: OpenApiResponse(description="Not Found")},
        summary="Retrieve a Tip by ID"
    )
    def retrieve(self, request, pk=None):
        try:
            tip_id = uuid.UUID(pk)
            output_dto = self._get_use_case.execute(tip_id=tip_id)
            return Response(output_dto.__dict__, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=UpdateTipInputSerializer,
        responses={200: TipOutputSerializer, 404: OpenApiResponse(description="Not Found")},
        summary="Update a Tip"
    )
    def update(self, request, pk=None):
        try:
            tip_id = uuid.UUID(pk)
            serializer = UpdateTipInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            input_dto = UpdateTipInputDTO(id=tip_id, **serializer.validated_data)
            output_dto = self._update_use_case.execute(input_dto)
            
            return Response(output_dto.__dict__, status=status.HTTP_200_OK)
        except ValueError as e:
            if "not found" in str(e).lower():
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": "Invalid input."}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={204: OpenApiResponse(description="No Content"), 404: OpenApiResponse(description="Not Found")},
        summary="Delete a Tip"
    )
    def destroy(self, request, pk=None):
        try:
            tip_id = uuid.UUID(pk)
            self._delete_use_case.execute(tip_id=tip_id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
