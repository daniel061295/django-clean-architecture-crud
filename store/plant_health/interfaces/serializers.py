from rest_framework import serializers

class AnalyzePlantHealthInputSerializer(serializers.Serializer):
    """
    Serializer for the plant health analysis input.
    """
    photo = serializers.ImageField(required=True)

class PlantHealthAnalysisResponseSerializer(serializers.Serializer):
    """
    Serializer for the plant health analysis response.
    """
    is_healthy = serializers.BooleanField()
    diagnosis = serializers.CharField()
    confidence = serializers.FloatField()
    treatment = serializers.ListField(child=serializers.CharField())
    urgency_level = serializers.CharField()
