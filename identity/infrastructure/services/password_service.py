"""
Password and Token Infrastructure Services — Django Implementations.
"""
from uuid import UUID

from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from identity.domain.interfaces import PasswordHasherInterface, PasswordTokenServiceInterface
from identity.infrastructure.models import CustomUserModel


class DjangoPasswordHasher(PasswordHasherInterface):
    """Django implementation of PasswordHasherInterface."""

    def make_password(self, password: str) -> str:
        """Hashes a plain text password using Django's default hasher."""
        return make_password(password)

    def check_password(self, password: str, encoded: str) -> bool:
        """Verifies a plain text password against a hash."""
        return check_password(password, encoded)


class DjangoPasswordTokenService(PasswordTokenServiceInterface):
    """Django implementation of PasswordTokenServiceInterface using default_token_generator."""

    def generate_token(self, user_id: UUID) -> str:
        """Generates a secure password reset token for the given user."""
        try:
            user = CustomUserModel.objects.get(id=user_id)
            return default_token_generator.make_token(user)
        except CustomUserModel.DoesNotExist:
            return ""

    def validate_token(self, user_id: UUID, token: str) -> bool:
        """Validates if the provided token is valid for the given user."""
        try:
            user = CustomUserModel.objects.get(id=user_id)
            return default_token_generator.check_token(user, token)
        except CustomUserModel.DoesNotExist:
            return False
