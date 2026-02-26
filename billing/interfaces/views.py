"""
Billing Interface Views — DRF Views for billing REST endpoints.

Public endpoints require authentication (IsAuthenticated).
Admin endpoints additionally require IsAdminUser.
Views are dumb — all logic delegated to use cases.
"""
from uuid import UUID

from drf_spectacular.utils import extend_schema
from injector import inject
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from billing.application.dtos import (
    CancelSubscriptionInputDTO,
    ChangePlanInputDTO,
    CreatePlanInputDTO,
)
from billing.application.use_cases import (
    CancelSubscription,
    ChangePlan,
    CreatePlan,
    GetAvailablePlans,
    GetMySubscription,
)
from billing.interfaces.serializers import (
    ChangePlanInputSerializer,
    CreatePlanInputSerializer,
    MySubscriptionOutputSerializer,
    PlanOutputSerializer,
    SubscriptionOutputSerializer,
)


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

    @extend_schema(responses={204: None})
    def post(self, request: Request) -> Response:
        """Cancels the current user's active subscription."""
        input_dto = CancelSubscriptionInputDTO(user_id=request.user.id)
        self._cancel.execute(input_dto)
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Admin-only Views
# ---------------------------------------------------------------------------

class AdminCreatePlanView(APIView):
    """POST /billing/admin/plans — Creates a new plan (admin only)."""

    permission_classes = [IsAdminUser]

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
