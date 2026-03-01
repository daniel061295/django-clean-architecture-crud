"""
Billing URLs — Route configuration for billing REST endpoints.
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from billing.interfaces.views import (
    AdminCreatePlanView,
    AdminSubscriptionViewSet,
    CancelSubscriptionView,
    ChangePlanView,
    MySubscriptionView,
    PlansListView,
    SubscribeView,
)

# Router for AdminSubscriptionViewSet
router = DefaultRouter()
router.register(
    r"admin/subscriptions",
    AdminSubscriptionViewSet,
    basename="billing-admin-subscriptions"
)

urlpatterns = [
    # Public (authenticated) endpoints
    path("plans/", PlansListView.as_view(), name="billing-plans"),
    path("me/", MySubscriptionView.as_view(), name="billing-me"),
    path("change-plan/", ChangePlanView.as_view(), name="billing-change-plan"),
    path("cancel/", CancelSubscriptionView.as_view(), name="billing-cancel"),
    path("subscribe/", SubscribeView.as_view(), name="billing-subscribe"),
    
    # Admin-only endpoints
    path("admin/plans/", AdminCreatePlanView.as_view(), name="billing-admin-plans"),
]

# Add router URLs for admin subscriptions
urlpatterns += router.urls
