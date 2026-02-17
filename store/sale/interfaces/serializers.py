from decimal import Decimal
from rest_framework import serializers
from store.sale.application.dtos import CreateSaleDTO, SaleDetailDTO, AddSaleDetailDTO

class SaleDetailRequestSerializer(serializers.Serializer):
    plant_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))

class CreateSaleSerializer(serializers.Serializer):
    initial_items = SaleDetailRequestSerializer(many=True, required=False)

    def to_dto(self) -> CreateSaleDTO:
        items_data = self.validated_data.get("initial_items", [])
        items_dtos = [
            SaleDetailDTO(
                plant_item_id=item["plant_item_id"],
                quantity=item["quantity"],
                unit_price=item["unit_price"]
            )
            for item in items_data
        ]
        return CreateSaleDTO(initial_items=items_dtos)

class AddSaleDetailSerializer(serializers.Serializer):
    plant_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.01"))

    def to_dto(self, sale_id) -> AddSaleDetailDTO:
        return AddSaleDetailDTO(
            sale_id=sale_id,
            plant_item_id=self.validated_data["plant_item_id"],
            quantity=self.validated_data["quantity"],
            unit_price=self.validated_data["unit_price"]
        )

class SaleDetailResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    plant_item_id = serializers.UUIDField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2)

class SaleResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    date = serializers.DateTimeField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)
    status = serializers.CharField()
    created_at = serializers.DateTimeField()
    details = SaleDetailResponseSerializer(many=True)
