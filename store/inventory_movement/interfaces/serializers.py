from rest_framework import serializers
from store.inventory_movement.application.dtos import RegisterInventoryMovementDTO
from store.inventory_movement.domain.entities import MovementType

class RegisterInventoryMovementSerializer(serializers.Serializer):
    plant_item_id = serializers.UUIDField()
    movement_type = serializers.ChoiceField(choices=[(tag.name, tag.value) for tag in MovementType])
    quantity = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def to_dto(self) -> RegisterInventoryMovementDTO:
        return RegisterInventoryMovementDTO(
            plant_item_id=self.validated_data["plant_item_id"],
            movement_type=self.validated_data["movement_type"],
            quantity=self.validated_data["quantity"],
            reason=self.validated_data.get("reason")
        )

class InventoryMovementResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    plant_item_id = serializers.UUIDField()
    movement_type = serializers.CharField()
    quantity = serializers.IntegerField()
    reason = serializers.CharField(allow_null=True)
    timestamp = serializers.DateTimeField()
    created_at = serializers.DateTimeField()
