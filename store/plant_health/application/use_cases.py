"""
Plant Health Application Use Case — analyzes plant health images.

Enforces RBAC permission check, active subscription validation,
and daily scan limit enforcement before delegating to the AI service.
"""
import base64
import logging
from datetime import date

from injector import inject
"""
Plant Health Application Use Case — analyzes plant health images.

Enforces RBAC permission check, active subscription validation,
and daily scan limit enforcement before delegating to the AI service.
"""
import logging
from datetime import date

from injector import inject

from billing.domain.exceptions import NoActiveSubscriptionError, ScanLimitExceededError
from billing.domain.interfaces import DailyUsageRepository, PlanRepository, SubscriptionRepository
from identity.domain.exceptions import PermissionDeniedError, UserNotFoundError
from identity.domain.interfaces import UserRepository
from store.plant_health.application.dtos import AnalyzePlantHealthInputDTO, PlantHealthAnalysisResponseDTO
from store.plant_health.domain.interfaces import PlantHealthService
from store.history.application.use_cases import CreateHistoryUseCase
from store.history.application.dtos import CreateHistoryInputDTO
from core.domain.services import StorageServiceInterface

logger = logging.getLogger(__name__)

SCAN_PLANT_PERMISSION = "scan_plant"


class AnalyzePlantHealth:
    """
    Use Case for analyzing plant health from a photo.

    Flow:
        1. Verify user exists.
        2. Check 'scan_plant' permission via RBAC.
        3. Validate active subscription.
        4. Get the active plan's scan limit.
        5. Get (or create) today's DailyUsage record.
        6. Verify the daily limit has not been reached.
        7. Run the AI analysis.
        8. Save history record (silent failure allowed).
        9. Increment the daily scan counter and persist.
        10. Return the analysis DTO.
    """

    @inject
    def __init__(
        self,
        service: PlantHealthService,
        create_history_use_case: CreateHistoryUseCase,
        user_repository: UserRepository,
        subscription_repository: SubscriptionRepository,
        plan_repository: PlanRepository,
        daily_usage_repository: DailyUsageRepository,
        storage_service: StorageServiceInterface,
    ) -> None:
        self._service = service
        self._create_history_use_case = create_history_use_case
        self._user_repo = user_repository
        self._sub_repo = subscription_repository
        self._plan_repo = plan_repository
        self._usage_repo = daily_usage_repository
        self._storage_service = storage_service

    def execute(self, input_dto: AnalyzePlantHealthInputDTO) -> PlantHealthAnalysisResponseDTO:
        """
        Executes the plant health analysis with full SaaS guardrails.

        Args:
            input_dto: Contains the photo file and the requesting user_id.

        Returns:
            PlantHealthAnalysisResponseDTO: The analysis result.

        Raises:
            UserNotFoundError: If the user_id cannot be resolved.
            PermissionDeniedError: If the user lacks the 'scan_plant' permission.
            NoActiveSubscriptionError: If the user has no active subscription.
            ScanLimitExceededError: If the user has hit the daily scan limit.
        """
        # Step 1 — Verify user
        user = self._user_repo.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        # Step 2 — RBAC permission check
        if not user.has_permission(SCAN_PLANT_PERMISSION):
            raise PermissionDeniedError(
                f"User does not have the '{SCAN_PLANT_PERMISSION}' permission."
            )

        # Step 3 — Validate active subscription
        subscription = self._sub_repo.get_active_by_user(input_dto.user_id)
        if subscription is None:
            raise NoActiveSubscriptionError("No active subscription found. Please subscribe to a plan.")

        # Step 4 — Get plan details (scan limit)
        plan = self._plan_repo.get_by_id(subscription.plan_id)

        # Step 5 — Get today's usage (creates record if it doesn't exist yet)
        usage = self._usage_repo.get_or_create(input_dto.user_id, date.today())

        # Step 6 — Validate daily limit
        if usage.has_reached_limit(plan.scan_limit_per_day):
            raise ScanLimitExceededError(
                f"Daily scan limit of {plan.scan_limit_per_day} reached. "
                "Please upgrade your plan or try again tomorrow."
            )

        # Step 7 — Run AI analysis
        report = self._service.analyze_photo(input_dto.photo)

        # Step 8 — Save history silently
        import uuid
        from core.utils.images import optimize_image

        photo_url: str = ""
        r2_key: str = ""
        try:
            input_dto.photo.seek(0)
            photo_bytes = input_dto.photo.read()
            
            optimized_bytes = optimize_image(photo_bytes, max_size=(1080, 1080), quality=80)
            
            file_name = f"plant_health/{input_dto.user_id}_{uuid.uuid4().hex[:8]}.jpg"
            r2_key = self._storage_service.upload_file(optimized_bytes, file_name, "image/jpeg")

            history_dto = CreateHistoryInputDTO(
                is_healthy=report.is_healthy,
                title=report.title,
                diagnosis=report.diagnosis,
                confidence=report.confidence,
                treatment=report.treatment,
                urgency_level=report.urgency_level,
                photo=r2_key,
                user_id=str(input_dto.user_id),
            )
            self._create_history_use_case.execute(history_dto)
            photo_url = self._storage_service.get_signed_url(r2_key) or r2_key
        except Exception as e:
            logger.error("Failed to save plant health history: %s", str(e), exc_info=True)

        # Step 9 — Increment and persist usage
        usage.increment_scan()
        self._usage_repo.save(usage)

        # Step 10 — Return result DTO
        return PlantHealthAnalysisResponseDTO(
            is_healthy=report.is_healthy,
            title=report.title,
            diagnosis=report.diagnosis,
            confidence=report.confidence,
            treatment=report.treatment,
            urgency_level=report.urgency_level,
            photo=photo_url,  # Returning the URL for the frontend
        )
