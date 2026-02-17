from rest_framework import serializers
from store.category.application.dtos import CreateCategoryDTO, UpdateCategoryDTO

class CreateCategorySerializer(serializers.Serializer):
    """
    Serializer for creating a new Category.
    """
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def to_dto(self) -> CreateCategoryDTO:
        """
        Converts the validated data to a CreateCategoryDTO.

        Returns:
            CreateCategoryDTO with category data.
        """
        return CreateCategoryDTO(
            name=self.validated_data["name"],
            description=self.validated_data.get("description")
        )

class UpdateCategorySerializer(serializers.Serializer):
    """
    Serializer for updating a Category.
    """
    name = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    active = serializers.BooleanField(required=False)

    def to_dto(self, category_id) -> UpdateCategoryDTO:
        """
        Converts the validated data to an UpdateCategoryDTO.

        Args:
            category_id: UUID of the category to update.

        Returns:
            UpdateCategoryDTO with category data.
        """
        return UpdateCategoryDTO(
            id=category_id,
            name=self.validated_data.get("name"),
            description=self.validated_data.get("description"),
            active=self.validated_data.get("active")
        )

class CategoryResponseSerializer(serializers.Serializer):
    """
    Serializer for Category response.
    """
    id = serializers.UUIDField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
