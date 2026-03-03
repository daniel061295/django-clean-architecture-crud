"""
Billing Interface Views — DRF Views for billing REST endpoints.

Public endpoints require HasPermission('manage_subscriptions') for admin operations.
Views are dumb — all logic delegated to use cases.
"""
from datetime import datetime
from uuid import UUID

from drf_spectacular.utils import extend_schema, OpenApiResponse, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from injector import inject
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.application.dtos import (
    CancelSubscriptionInputDTO,
    ChangePlanInputDTO,
    CreateFreeSubscriptionForUserInputDTO,
    CreatePlanInputDTO,
    CreateSubscriptionInputDTO,
)
from billing.application.use_cases import (
    AssignProSubscription,
    CancelSubscription,
    ChangePlan,
    CreateFreeSubscriptionForNewUser,
    CreatePlan,
    CreateSubscription,
    GetAvailablePlans,
    GetMySubscription,
)
from billing.interfaces.serializers import (
    AdminSubscriptionOutputSerializer,
    ChangePlanInputSerializer,
    CreatePlanInputSerializer,
    CreateSubscriptionInputSerializer,
    MySubscriptionOutputSerializer,
    PlanOutputSerializer,
    SubscriptionOutputSerializer,
)
from identity.interfaces.permissions import HasPermission


class PlansListView(APIView):
    """GET /billing/plans — Returns all active plans (public, authenticated)."""

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self, get_plans: GetAvailablePlans = None, **kwargs) -> None:
        self._get_plans = get_plans
        super().__init__(**kwargs)

    @extend_schema(responses={200: PlanOutputSerializer(many=True)})
    def get(self, request: Request) -> Response:
        """Returns all active SaaS plans."""
        results = self._get_plans.execute()
        return Response(PlanOutputSerializer(results, many=True).data)


class MySubscriptionView(APIView):
    """GET /billing/me — Returns current user's subscription and today's usage."""

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self, get_my_subscription: GetMySubscription = None, **kwargs) -> None:
        self._get_my = get_my_subscription
        super().__init__(**kwargs)

    @extend_schema(responses={200: MySubscriptionOutputSerializer})
    def get(self, request: Request) -> Response:
        """Returns the current user's active plan, status, and today's scan usage."""
        result = self._get_my.execute(request.user.id)
        return Response(MySubscriptionOutputSerializer(result).data)


class ChangePlanView(APIView):
    """POST /billing/change-plan — Activates a new plan for the current user."""

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self, change_plan: ChangePlan = None, **kwargs) -> None:
        self._change_plan = change_plan
        super().__init__(**kwargs)

    @extend_schema(
        request=ChangePlanInputSerializer,
        responses={200: SubscriptionOutputSerializer},
    )
    def post(self, request: Request) -> Response:
        """Cancels the current plan and activates the requested plan."""
        serializer = ChangePlanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = ChangePlanInputDTO(
            user_id=request.user.id,
            plan_id=serializer.validated_data["plan_id"],
        )
        result = self._change_plan.execute(input_dto)
        return Response(SubscriptionOutputSerializer(result).data)


class CancelSubscriptionView(APIView):
    """POST /billing/cancel — Cancels the current user's subscription."""

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(self, cancel_subscription: CancelSubscription = None, **kwargs) -> None:
        self._cancel = cancel_subscription
        super().__init__(**kwargs)

    @extend_schema(request=None, responses={204: None})
    def post(self, request: Request) -> Response:
        """Cancels the current user's active subscription."""
        input_dto = CancelSubscriptionInputDTO(user_id=request.user.id)
        self._cancel.execute(input_dto)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Admin-only Views
# ---------------------------------------------------------------------------

class AdminCreatePlanView(APIView):
    """POST /billing/admin/plans — Creates a new plan (requires manage_subscriptions permission)."""

    permission_classes = [HasPermission]

    def get_permission_code(self) -> str:
        """Returns the required permission code for this endpoint."""
        return "manage_subscriptions"

    @inject
    def __init__(self, create_plan: CreatePlan = None, **kwargs) -> None:
        self._create_plan = create_plan
        super().__init__(**kwargs)

    @extend_schema(request=CreatePlanInputSerializer, responses={201: PlanOutputSerializer})
    def post(self, request: Request) -> Response:
        """Creates a new SaaS plan."""
        serializer = CreatePlanInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_dto = CreatePlanInputDTO(**serializer.validated_data)
        result = self._create_plan.execute(input_dto)
        return Response(PlanOutputSerializer(result).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Public Subscription Endpoint
# ---------------------------------------------------------------------------

class SubscribeView(APIView):
    """POST /billing/subscribe/ — Creates first subscription for current user."""

    permission_classes = [IsAuthenticated]

    @inject
    def __init__(
        self,
        create_subscription: CreateSubscription = None,
        create_free_subscription: CreateFreeSubscriptionForNewUser = None,
        **kwargs
    ) -> None:
        self._create_subscription = create_subscription
        self._create_free = create_free_subscription
        super().__init__(**kwargs)

    @extend_schema(
        request=CreateSubscriptionInputSerializer,
        responses={
            201: SubscriptionOutputSerializer,
            400: OpenApiResponse(description="User already has active subscription"),
        },
    )
    def post(self, request: Request) -> Response:
        """
        Creates the first subscription for the current user.
        
        If plan_id is provided, subscribes to that plan.
        If plan_id is not provided, subscribes to FREE plan by default.
        """
        if request.data.get("plan_id"):
            # User specified a plan
            serializer = CreateSubscriptionInputSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            input_dto = CreateSubscriptionInputDTO(
                user_id=request.user.id,
                plan_id=serializer.validated_data["plan_id"],
                start_date=datetime.utcnow(),
            )
            result = self._create_subscription.execute(input_dto)
        else:
            # Use FREE plan by default
            input_dto = CreateFreeSubscriptionForUserInputDTO(user_id=request.user.id)
            result = self._create_free.execute(input_dto)

        return Response(SubscriptionOutputSerializer(result).data, status=status.HTTP_201_CREATED)


# ---------------------------------------------------------------------------
# Admin Subscription Management
# ---------------------------------------------------------------------------

@extend_schema_view(
    list=extend_schema(responses={200: AdminSubscriptionOutputSerializer(many=True)}),
    retrieve=extend_schema(
        parameters=[OpenApiParameter("pk", OpenApiTypes.UUID, OpenApiParameter.PATH)],
        responses={200: AdminSubscriptionOutputSerializer}
    ),
)
class AdminSubscriptionViewSet(viewsets.ViewSet):
    """ViewSet for admin subscription management (requires manage_subscriptions permission)."""

    permission_classes = [HasPermission]

    def get_permission_code(self) -> str:
        """Returns the required permission code for this endpoint."""
        return "manage_subscriptions"

    @inject
    def __init__(self, assign_pro_subscription: AssignProSubscription = None, create_free_subscription: CreateFreeSubscriptionForNewUser = None, **kwargs):
        self._assign_pro = assign_pro_subscription
        self._create_free = create_free_subscription
        super().__init__(**kwargs)

    def list(self, request: Request) -> Response:
        """Lists all subscriptions."""
        subscriptions = SubscriptionModel.objects.all().select_related("user", "plan")

        return Response(AdminSubscriptionOutputSerializer(subscriptions, many=True).data)

    def retrieve(self, request: Request, pk: str = None) -> Response:
        """Gets subscription details for a specific user."""
        subscription = SubscriptionModel.objects.filter(
            user_id=pk, status__in=[SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value]
        ).select_related("plan").first()

        if subscription is None:
            return Response(
                {"error": "No active subscription found"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(AdminSubscriptionOutputSerializer(subscription).data)

    @action(detail=True, methods=["post"], url_path="assign-pro")
    def assign_pro(self, request: Request, pk: str = None) -> Response:
        """Assigns PRO subscription to a user (cancels any existing subscription)."""
        try:
            from uuid import UUID
            user_id = UUID(pk)
            result = self._assign_pro.execute(user_id)
            return Response(
                {
                    "message": f"PRO subscription assigned to user {pk}",
                    "subscription": SubscriptionOutputSerializer(result).data,
                },
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="assign-free")
    def assign_free(self, request: Request, pk: str = None) -> Response:
        """Assigns FREE subscription to a user (permanent, no expiration)."""
        try:
            from uuid import UUID
            from billing.application.dtos import CreateFreeSubscriptionForUserInputDTO
            user_id = UUID(pk)
            input_dto = CreateFreeSubscriptionForUserInputDTO(user_id=user_id)
            result = self._create_free.execute(input_dto)
            return Response(
                {
                    "message": f"FREE subscription assigned to user {pk} (permanent, no expiration)",
                    "subscription": SubscriptionOutputSerializer(result).data,
                },
                status=status.HTTP_201_CREATED if result.id else status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request: Request, pk: str = None) -> Response:
        """Activates FREE subscription for a specific user (legacy endpoint)."""
        # Legacy endpoint - use assign-free instead
        return self.assign_free(request, pk)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request: Request, pk: str = None) -> Response:
        """Cancels subscription for a specific user."""
        SubscriptionModel.objects.filter(
            user_id=pk, status__in=[SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value]
        ).update(status=SubscriptionStatus.CANCELED.value)

        return Response(
            {"message": f"Subscription canceled for user {pk}"},
            status=status.HTTP_200_OK
        )
