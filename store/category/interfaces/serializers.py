from rest_framework import serializers
from store.category.application.dtos import CreateCategoryDTO, UpdateCategoryDTO

class CreateCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def to_dto(self) -> CreateCategoryDTO:
        return CreateCategoryDTO(
            name=self.validated_data["name"],
            description=self.validated_data.get("description")
        )

class UpdateCategorySerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    active = serializers.BooleanField(required=False)

    def to_dto(self, category_id) -> UpdateCategoryDTO:
        return UpdateCategoryDTO(
            id=category_id,
            name=self.validated_data.get("name"),
            description=self.validated_data.get("description"),
            active=self.validated_data.get("active")
        )

class CategoryResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
