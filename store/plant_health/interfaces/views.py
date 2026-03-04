from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from injector import inject
from drf_spectacular.utils import extend_schema, OpenApiResponse

from billing.interfaces.permissions import HasSubscriptionScanPermission
from store.plant_health.application.use_cases import AnalyzePlantHealth
from store.plant_health.application.dtos import AnalyzePlantHealthInputDTO
from store.plant_health.interfaces.serializers import AnalyzePlantHealthInputSerializer, PlantHealthAnalysisResponseSerializer
from store.plant_health.domain.exceptions import LowConfidenceError, InvalidPlantImageError, ServiceUnavailableError


class PlantHealthView(viewsets.ViewSet):
    """
    ViewSet for Plant Health Analysis.

    Requires HasSubscriptionScanPermission which verifies:
    - User is authenticated
    - User has 'scan_plant' permission
    - User has active subscription
    - User has not exceeded daily scan limit
    """

    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (HasSubscriptionScanPermission,)

    @inject
    def __init__(self, analyze_use_case: AnalyzePlantHealth = None, **kwargs):
        self.analyze_use_case = analyze_use_case
        super().__init__(**kwargs)

    @extend_schema(
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "photo": {"type": "string", "format": "binary"}
                },
                "required": ["photo"]
            }
        },
        responses={
            200: PlantHealthAnalysisResponseSerializer,
            400: OpenApiResponse(description="Bad Request"),
            422: OpenApiResponse(description="Low Confidence - Please retake photo")
        }
    )
    def create(self, request):
        """
        Analyzes a plant photo to detect health issues and pests.
        """
        serializer = AnalyzePlantHealthInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        photo_file = serializer.validated_data['photo']
        
        # Convert uploaded file to BinaryIO (it is already file-like)
        input_dto = AnalyzePlantHealthInputDTO(photo=photo_file, user_id=request.user.id)

        try:
            result = self.analyze_use_case.execute(input_dto)
            
            response_serializer = PlantHealthAnalysisResponseSerializer(result)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except LowConfidenceError as e:
             return Response(
                {"error": str(e), "code": "LOW_CONFIDENCE"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except InvalidPlantImageError as e:
            return Response(
                {
                    "is_healthy": False,
                    "title": "Imagen no procesable",
                    "diagnosis": str(e),
                    "confidence": 0.0,
                    "treatment": [],
                    "urgency_level": "Low"
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        except ServiceUnavailableError as e:
            return Response(
                {"error": str(e), "code": "AI_UNAVAILABLE"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            # General error handling
            return Response(
                {"error": "An unexpected error occurred during analysis.", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
