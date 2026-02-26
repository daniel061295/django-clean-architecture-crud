"""
Billing URLs — Route configuration for billing REST endpoints.
"""
from django.urls import path

from billing.interfaces.views import (
    AdminCreatePlanView,
    CancelSubscriptionView,
    ChangePlanView,
    MySubscriptionView,
    PlansListView,
)

urlpatterns = [
    # Public (authenticated) endpoints
    path("plans/", PlansListView.as_view(), name="billing-plans"),
    path("me/", MySubscriptionView.as_view(), name="billing-me"),
    path("change-plan/", ChangePlanView.as_view(), name="billing-change-plan"),
    path("cancel/", CancelSubscriptionView.as_view(), name="billing-cancel"),
    # Admin-only endpoints
    path("admin/plans/", AdminCreatePlanView.as_view(), name="billing-admin-plans"),
]
