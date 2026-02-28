from rest_framework import serializers

class CreateHistoryInputSerializer(serializers.Serializer):
    """
    Serializer to map JSON request data to CreateHistoryInputDTO.
    """
    is_healthy = serializers.BooleanField()
    title = serializers.CharField(max_length=255)
    diagnosis = serializers.CharField(max_length=255)
    confidence = serializers.FloatField()
    treatment = serializers.ListField(
        child=serializers.CharField()
    )
    urgency_level = serializers.CharField(max_length=50)
    photo = serializers.CharField()
    user_id = serializers.CharField(max_length=36)
