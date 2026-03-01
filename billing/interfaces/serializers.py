"""
Billing Interface Serializers — DRF Serializers for billing REST endpoints.
"""
from typing import Optional

from rest_framework import serializers


class PlanOutputSerializer(serializers.Serializer):
    """Serializes a SaaS plan for API responses."""
    id = serializers.CharField()
    name = serializers.CharField()
    price = serializers.FloatField()
    scan_limit_per_day = serializers.IntegerField(allow_null=True)
    ads_enabled = serializers.BooleanField()
    features = serializers.DictField()
    is_active = serializers.BooleanField()


class CreatePlanInputSerializer(serializers.Serializer):
    """Deserializes plan creation requests (admin only)."""
    name = serializers.CharField(max_length=100)
    price = serializers.FloatField(min_value=0)
    scan_limit_per_day = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    ads_enabled = serializers.BooleanField(default=True)
    features = serializers.DictField(required=False, default=dict)


class ChangePlanInputSerializer(serializers.Serializer):
    """Deserializes a plan change request."""
    plan_id = serializers.UUIDField()


class MySubscriptionOutputSerializer(serializers.Serializer):
    """Serializes the composite 'my subscription' response for /billing/me."""
    plan_name = serializers.CharField()
    plan_id = serializers.CharField()
    status = serializers.CharField()
    scan_limit_per_day = serializers.IntegerField(allow_null=True)
    ads_enabled = serializers.BooleanField()
    usage_today = serializers.IntegerField()
    features = serializers.DictField()


class SubscriptionOutputSerializer(serializers.Serializer):
    """Serializes a Subscription for API responses."""
    id = serializers.CharField()
    user_id = serializers.CharField()
    plan_id = serializers.CharField()
    status = serializers.CharField()
    start_date = serializers.CharField()
    end_date = serializers.CharField(allow_null=True)
    external_id = serializers.CharField(allow_null=True)


class CreateSubscriptionInputSerializer(serializers.Serializer):
    """Deserializes subscription creation requests."""
    plan_id = serializers.UUIDField(required=False, allow_null=True)
    
    def get_plan_id(self) -> Optional[UUID]:
        """Returns the plan_id if provided, None otherwise."""
        return self.validated_data.get("plan_id")


class AdminSubscriptionOutputSerializer(serializers.Serializer):
    """Serializes subscription for admin listing with user details."""
    id = serializers.CharField()
    user_id = serializers.CharField()
    user_email = serializers.CharField(source="user.email")
    user_username = serializers.CharField(source="user.username")
    plan_id = serializers.CharField()
    plan_name = serializers.CharField(source="plan.name")
    status = serializers.CharField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField(allow_null=True)
