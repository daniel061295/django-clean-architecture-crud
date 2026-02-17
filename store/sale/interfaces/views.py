from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from injector import inject
from uuid import UUID
from store.sale.application.use_cases.create_sale import CreateSale
from store.sale.application.use_cases.add_sale_detail import AddSaleDetail
from store.sale.application.use_cases.complete_sale import CompleteSale
from store.sale.application.use_cases.list_sales import ListSales
from store.sale.application.use_cases.get_sale import GetSale
from store.sale.interfaces.serializers import (
    CreateSaleSerializer, 
    SaleResponseSerializer,
    AddSaleDetailSerializer,
    SaleDetailResponseSerializer
)
from drf_spectacular.utils import extend_schema, OpenApiParameter

class SaleView(viewsets.ViewSet):
    """
    ViewSet for managing Sales.
    """

    @inject
    def __init__(self, 
                 create_use_case: CreateSale = None,
                 add_detail_use_case: AddSaleDetail = None,
                 complete_use_case: CompleteSale = None,
                 list_use_case: ListSales = None,
                 get_use_case: GetSale = None,
                 **kwargs):
        self.create_use_case = create_use_case
        self.add_detail_use_case = add_detail_use_case
        self.complete_use_case = complete_use_case
        self.list_use_case = list_use_case
        self.get_use_case = get_use_case
        super().__init__(**kwargs)

    @extend_schema(
        parameters=[
            OpenApiParameter(name="page", description="Page number", required=False, type=int),
            OpenApiParameter(name="page_size", description="Items per page", required=False, type=int),
            OpenApiParameter(name="status", description="Filter by status (PENDING, COMPLETED, CANCELED)", required=False, type=str),
        ],
        responses={200: SaleResponseSerializer(many=True)}
    )
    def list(self, request):
        """List all sales with pagination and filtering."""
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))
        filters = {
            "status": request.query_params.get("status")
        }

        result, total_count = self.list_use_case.execute(page, page_size, filters)
        serializer = SaleResponseSerializer(result, many=True)
        return Response({
            "data": serializer.data,
            "total": total_count,
            "page": page,
            "page_size": page_size
        })

    @extend_schema(request=CreateSaleSerializer, responses={201: SaleResponseSerializer})
    def create(self, request):
        """Starts a new Sale (PENDING)."""
        serializer = CreateSaleSerializer(data=request.data)
        if serializer.is_valid():
            try:
                dto = serializer.to_dto()
                result = self.create_use_case.execute(dto)
                response_serializer = SaleResponseSerializer(result)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={200: SaleResponseSerializer})
    def retrieve(self, request, pk=None):
        """Retrieve a sale by ID."""
        try:
            sale_id = UUID(pk)
        except ValueError:
             return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)

        result = self.get_use_case.execute(sale_id)
        if not result:
            return Response({"error": "Sale not found"}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = SaleResponseSerializer(result)
        return Response(serializer.data)

    @extend_schema(request=AddSaleDetailSerializer, responses={200: SaleResponseSerializer})
    @action(detail=True, methods=["post"], url_path="items")
    def add_item(self, request, pk=None):
        """Adds an item to an existing Sale."""
        try:
            sale_id = UUID(pk)
        except ValueError:
             return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = AddSaleDetailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                dto = serializer.to_dto(sale_id)
                result = self.add_detail_use_case.execute(dto)
                response_serializer = SaleResponseSerializer(result)
                return Response(response_serializer.data)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(responses={200: SaleResponseSerializer})
    @action(detail=True, methods=["post"], url_path="complete")
    def complete(self, request, pk=None):
        """Completes the sale and updates inventory."""
        try:
            sale_id = UUID(pk)
        except ValueError:
             return Response({"error": "Invalid UUID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = self.complete_use_case.execute(sale_id)
            response_serializer = SaleResponseSerializer(result)
            return Response(response_serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
