from injector import inject
from identity.domain.exceptions import UserNotFoundError
from identity.domain.interfaces import (
    UserRepository,
    PasswordHasherInterface,
    PasswordTokenServiceInterface,
    EmailServiceInterface,
)
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

class ChangeUserPassword:
    """Changes the password for an authenticated user."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasherInterface,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    def execute(self, input_dto: "ChangeUserPasswordInputDTO") -> None:
        from identity.domain.exceptions import InvalidPasswordError
        
        user = self._user_repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        # Let's get the hashed password from db model
        from identity.infrastructure.models import CustomUserModel
        user_model = CustomUserModel.objects.get(id=input_dto.user_id)
        
        if not self._password_hasher.check_password(input_dto.old_password, user_model.password):
            raise InvalidPasswordError("La contraseña actual es incorrecta.")

        hashed_new_password = self._password_hasher.make_password(input_dto.new_password)
        self._user_repository.update_password(input_dto.user_id, hashed_new_password)


class RequestPasswordReset:
    """Handles requesting a password reset and sending the email."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: PasswordTokenServiceInterface,
        email_service: EmailServiceInterface,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service
        self._email_service = email_service

    def execute(self, input_dto: "RequestPasswordResetInputDTO", frontend_url: str) -> None:
        user = self._user_repository.get_by_email(input_dto.email)
        if user is None:
            # We return silently to prevent email enumeration attacks
            return

        token = self._token_service.generate_token(user.id)
        if not token:
            return
            
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        
        # Build the final URL (Assuming frontend_url already has the domain like http://localhost:3000/reset-password)
        reset_link = f"{frontend_url}?uid={uidb64}&token={token}"
        
        self._email_service.send_password_reset_email(user.email, reset_link)


class ConfirmPasswordReset:
    """Confirms and executes a password reset."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        token_service: PasswordTokenServiceInterface,
        password_hasher: PasswordHasherInterface,
    ) -> None:
        self._user_repository = user_repository
        self._token_service = token_service
        self._password_hasher = password_hasher

    def execute(self, input_dto: "ConfirmPasswordResetInputDTO") -> None:
        from identity.domain.exceptions import InvalidTokenError
        
        user = self._user_repository.get_by_id(input_dto.user_id)
        if user is None:
            raise InvalidTokenError("El token es inválido o ha expirado.")

        if not self._token_service.validate_token(input_dto.user_id, input_dto.token):
            raise InvalidTokenError("El token es inválido o ha expirado.")

        hashed_password = self._password_hasher.make_password(input_dto.new_password)
        self._user_repository.update_password(input_dto.user_id, hashed_password)
