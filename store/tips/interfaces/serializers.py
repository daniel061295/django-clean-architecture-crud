from rest_framework import serializers

class CreateTipInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    icon = serializers.CharField(max_length=100)

class UpdateTipInputSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    icon = serializers.CharField(max_length=100, required=False)

class TipOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    title = serializers.CharField()
    description = serializers.CharField()
    icon = serializers.CharField()
    created_at = serializers.DateTimeField()
