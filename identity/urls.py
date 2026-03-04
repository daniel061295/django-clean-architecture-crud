"""
Identity URLs — Route configuration for RBAC and JWT auth endpoints.
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from identity.interfaces.views import (
    MyPermissionsView,
    UserProfileView,
    UserAvatarView,
    PermissionViewSet,
    RoleViewSet,
    UserViewSet,
    GoogleLoginView,
    ChangePasswordView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

router = DefaultRouter()
router.register(r"permissions", PermissionViewSet, basename="permission")
router.register(r"roles", RoleViewSet, basename="role")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("users/password-reset-request/", PasswordResetRequestView.as_view(), name="identity-password-reset-request"),
    path("users/password-reset-confirm/", PasswordResetConfirmView.as_view(), name="identity-password-reset-confirm"),
    path("", include(router.urls)),
    path("me/", UserProfileView.as_view(), name="identity-me-profile"),
    path("me/avatar/", UserAvatarView.as_view(), name="identity-me-avatar"),
    path("me/permissions/", MyPermissionsView.as_view(), name="identity-me-permissions"),
    path("me/change-password/", ChangePasswordView.as_view(), name="identity-me-change-password"),
]

# Auth token endpoints — registered separately in config/urls.py under /auth/
auth_urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("google/", GoogleLoginView.as_view(), name="token_google"),
]
