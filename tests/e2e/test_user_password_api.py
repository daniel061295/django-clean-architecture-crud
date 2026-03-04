import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from identity.infrastructure.models import CustomUserModel
from identity.infrastructure.services.password_service import DjangoPasswordTokenService

@pytest.mark.django_db
class TestUserPasswordAPI:
    def setup_method(self):
        self.client = APIClient()
        self.user = CustomUserModel.objects.create_user(
            email="test@example.com",
            username="testuser",
            password="oldpassword123"
        )
        self.change_password_url = "/identity/me/change-password/"
        self.reset_request_url = "/identity/users/password-reset-request/"
        self.reset_confirm_url = "/identity/users/password-reset-confirm/"

    def test_change_password_success(self):
        # Authenticate
        self.client.force_authenticate(user=self.user)
        
        payload = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123"
        }
        response = self.client.post(self.change_password_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password changed
        self.user.refresh_from_db()
        assert self.user.check_password("newpassword123") is True

    def test_change_password_invalid_old_password(self):
        self.client.force_authenticate(user=self.user)
        
        payload = {
            "old_password": "wrongpassword",
            "new_password": "newpassword123"
        }
        response = self.client.post(self.change_password_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_change_password_unauthenticated(self):
        payload = {
            "old_password": "oldpassword123",
            "new_password": "newpassword123"
        }
        response = self.client.post(self.change_password_url, payload, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_password_reset_request_success(self):
        payload = {"email": "test@example.com"}
        response = self.client.post(self.reset_request_url, payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 1
        assert "test@example.com" in mail.outbox[0].to

    def test_password_reset_request_nonexistent_email(self):
        payload = {"email": "nobody@example.com"}
        response = self.client.post(self.reset_request_url, payload, format='json')
        
        # Should still return 200 OK to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK
        assert len(mail.outbox) == 0

    def test_password_reset_confirm_success(self):
        # 1. Generate token and uid
        token_service = DjangoPasswordTokenService()
        token = token_service.generate_token(self.user.id)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        
        payload = {
            "uidb64": uidb64,
            "token": token,
            "new_password": "resetpassword123"
        }
        response = self.client.post(self.reset_confirm_url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK
        
        # Verify password changed
        self.user.refresh_from_db()
        assert self.user.check_password("resetpassword123") is True

    def test_password_reset_confirm_invalid_token(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        
        payload = {
            "uidb64": uidb64,
            "token": "invalid-token",
            "new_password": "resetpassword123"
        }
        response = self.client.post(self.reset_confirm_url, payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
