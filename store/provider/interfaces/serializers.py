from rest_framework import serializers
from store.provider.application.dtos import CreateProviderDTO, UpdateProviderDTO

class CreateProviderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def to_dto(self) -> CreateProviderDTO:
        return CreateProviderDTO(
            name=self.validated_data["name"],
            phone=self.validated_data.get("phone"),
            email=self.validated_data.get("email"),
            address=self.validated_data.get("address")
        )

class UpdateProviderSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True, allow_null=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    active = serializers.BooleanField(required=False)

    def to_dto(self, provider_id) -> UpdateProviderDTO:
        return UpdateProviderDTO(
            id=provider_id,
            name=self.validated_data.get("name"),
            phone=self.validated_data.get("phone"),
            email=self.validated_data.get("email"),
            address=self.validated_data.get("address"),
            active=self.validated_data.get("active")
        )

class ProviderResponseSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    email = serializers.CharField(allow_null=True)
    address = serializers.CharField(allow_null=True)
    active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
