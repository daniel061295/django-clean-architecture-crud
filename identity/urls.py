"""
Identity URLs — Route configuration for RBAC and JWT auth endpoints.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from identity.interfaces.views import (
    MyPermissionsView,
    PermissionViewSet,
    RoleViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("me/permissions/", MyPermissionsView.as_view(), name="identity-me-permissions"),
]

# Auth token endpoints — registered separately in config/urls.py under /auth/
auth_urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
]
