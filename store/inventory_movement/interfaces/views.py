from rest_framework import viewsets, status
from rest_framework.response import Response
from injector import inject
from uuid import UUID
from store.inventory_movement.application.use_cases.register_inventory_movement import RegisterInventoryMovement
from store.inventory_movement.application.use_cases.list_inventory_movements import ListInventoryMovements
from store.inventory_movement.application.use_cases.get_inventory_movement import GetInventoryMovement
from store.inventory_movement.interfaces.serializers import (
    RegisterInventoryMovementSerializer, 
    InventoryMovementResponseSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter

class InventoryMovementView(viewsets.ViewSet):
    """
    ViewSet for managing Inventory Movements.
    """

    @inject
    def __init__(self, 
                 register_use_case: RegisterInventoryMovement = None,
                 list_use_case: ListInventoryMovements = None,
                 get_use_case: GetInventoryMovement = None,
                 **kwargs):
        self.register_use_case = register_use_case
        self.list_use_case = list_use_case
        self.get_use_case = get_use_case
        super().__init__(**kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="page", description="Page number", required=False, type=int),
            OpenApiParameter(name="page_size", description="Items per page", required=False, type=int),
            OpenApiParameter(name="plant_item_id", description="Filter by plant item ID", required=False, type=str),
            OpenApiParameter(name="movement_type", description="Filter by movement type (ENTRADA, SALIDA, AJUSTE)", required=False, type=str),
        ],
        responses={200: InventoryMovementResponseSerializer(many=True)}
    )
    def list(self, request):
        """List inventory movements with pagination and filtering."""
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        filters = {
            "plant_item_id": request.query_params.get("plant_item_id"),
            "movement_type": request.query_params.get("movement_type")
        }

        result, total_count = self.list_use_case.execute(page, page_size, filters)
        serializer = InventoryMovementResponseSerializer(result, many=True)
        return Response({
            "data": serializer.data,
            "total": total_count,
            "page": page,
            "page_size": page_size
        })

    @extend_schema(request=RegisterInventoryMovementSerializer, responses={201: InventoryMovementResponseSerializer})
    def create(self, request):
        """Registers a new Inventory Movement."""
        serializer = RegisterInventoryMovementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                dto = serializer.to_dto()
                result = self.register_use_case.execute(dto)
                response_serializer = InventoryMovementResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={200: InventoryMovementResponseSerializer})
    def retrieve(self, request, pk=None):
        """Retrieve an inventory movement by ID."""
        try:
            movement_id = UUID(pk)
        except ValueError:
             return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)

        result = self.get_use_case.execute(movement_id)
        if not result:
            return Response({"error": "Inventory Movement not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = InventoryMovementResponseSerializer(result)
        return Response(serializer.data)
