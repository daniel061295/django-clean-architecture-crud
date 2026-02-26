"""
URL configuration for config project.
"""
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib import admin
from django.urls import path, include
from identity.urls import auth_urlpatterns

urlpatterns = [
    path("admin/", admin.site.urls),
    # Store endpoints
    path("api/", include("store.urls")),
    # Identity & RBAC endpoints
    path("identity/", include("identity.urls")),
    # Billing & SaaS endpoints
    path("billing/", include("billing.urls")),
    # JWT auth endpoints
    path("auth/", include((auth_urlpatterns, "auth"))),
    # API schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
