from rest_framework import serializers
from store.plant_item.application.dtos import CreatePlantItemDTO, UpdatePlantItemDTO


class CreatePlantItemSerializer(serializers.Serializer):
    """
    Serializer for creating a new PlantItem.
    Validates input data for creation.
    """

    name = serializers.CharField(max_length=255)
    description = serializers.CharField()
    price = serializers.FloatField()
    stock = serializers.IntegerField()

    def to_dto(self) -> CreatePlantItemDTO:
        return CreatePlantItemDTO(
            name=self.validated_data["name"],
            description=self.validated_data["description"],
            price=self.validated_data["price"],
            stock=self.validated_data["stock"],
        )


class UpdatePlantItemSerializer(serializers.Serializer):
    """
    Serializer for updating an existing PlantItem.
    All fields are optional to allow partial updates.
    """

    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    price = serializers.FloatField(required=False)
    stock = serializers.IntegerField(required=False)

    def to_dto(self) -> UpdatePlantItemDTO:
        return UpdatePlantItemDTO(
            name=self.validated_data.get("name"),
            description=self.validated_data.get("description"),
            price=self.validated_data.get("price"),
            stock=self.validated_data.get("stock"),
        )


class PlantItemResponseSerializer(serializers.Serializer):
    """
    Serializer for PlantItem responses.
    Formats the domain entity for the API response.
    """

    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.FloatField()
    stock = serializers.IntegerField()
    is_available = serializers.BooleanField()
    created_at = serializers.DateTimeField()
