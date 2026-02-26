from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..application.use_cases import CreateHistoryUseCase, GetHistoryUseCase, GetAllHistoryUseCase, DeleteHistoryUseCase, DeleteAllHistoryUseCase
from ..application.dtos import CreateHistoryInputDTO, GetHistoryInputDTO
from .serializers import CreateHistoryInputSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from dataclasses import asdict
from store.di import StoreModule
from injector import Injector

class HistoryListView(APIView):
    """
    API View to manage History List operations.
    """

    @extend_schema(
        request=CreateHistoryInputSerializer,
        responses={
            201: OpenApiResponse(description="History created"),
            400: OpenApiResponse(description="Bad request")
        },
        description="Creates a new AI diagnosis history record."
    )
    def post(self, request):
        serializer = CreateHistoryInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreateHistoryInputDTO(**serializer.validated_data)
        
        # Dependency Injection
        injector = Injector([StoreModule()])
        use_case = injector.get(CreateHistoryUseCase)

        output_dto = use_case.execute(input_dto)
        return Response(asdict(output_dto), status=status.HTTP_201_CREATED)

    @extend_schema(
        responses={
            200: OpenApiResponse(description="List of history records"),
        },
        description="Retrieves a list of all diagnosis history records."
    )
    def get(self, request):
        injector = Injector([StoreModule()])
        use_case = injector.get(GetAllHistoryUseCase)
        output_dtos = use_case.execute()
        return Response([asdict(dto) for dto in output_dtos], status=status.HTTP_200_OK)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="All history deleted successfully"),
        },
        description="Deletes all history records."
    )
    def delete(self, request):
        injector = Injector([StoreModule()])
        use_case = injector.get(DeleteAllHistoryUseCase)
        use_case.execute()
        return Response(status=status.HTTP_204_NO_CONTENT)


class HistoryDetailView(APIView):
    """
    API View to manage History Detail operations.
    """

    @extend_schema(
        responses={
            200: OpenApiResponse(description="A single history record"),
            404: OpenApiResponse(description="History not found"),
        },
        description="Retrieves a history record by its ID."
    )
    def get(self, request, id):
        injector = Injector([StoreModule()])
        use_case = injector.get(GetHistoryUseCase)
        input_dto = GetHistoryInputDTO(id=id)
        try:
            output_dto = use_case.execute(input_dto)
            return Response(asdict(output_dto), status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        responses={
            204: OpenApiResponse(description="History deleted successfully"),
            404: OpenApiResponse(description="History not found"),
        },
        description="Deletes a history record by its ID."
    )
    def delete(self, request, id):
        injector = Injector([StoreModule()])
        use_case = injector.get(DeleteHistoryUseCase)
        input_dto = GetHistoryInputDTO(id=id)
        try:
            use_case.execute(input_dto)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

