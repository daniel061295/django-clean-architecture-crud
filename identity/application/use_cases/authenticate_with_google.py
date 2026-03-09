from injector import inject

from identity.application.dtos import AuthenticateWithGoogleInputDTO, UserOutputDTO
from identity.domain.interfaces import GoogleAuthServiceInterface, RoleRepository, UserRepository
from billing.application.use_cases import CreateFreeSubscriptionForNewUser
from ._helpers import _user_to_dto

class AuthenticateWithGoogle:
    """Authenticates a user via Google OAuth, creating a new local user if they don't exist."""

    @inject
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        google_service: GoogleAuthServiceInterface,
        create_free_subscription: CreateFreeSubscriptionForNewUser = None,
    ) -> None:
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._google_service = google_service
        self._create_free_subscription = create_free_subscription

    def execute(self, input_dto: AuthenticateWithGoogleInputDTO) -> UserOutputDTO:
        # Verify token
        payload = self._google_service.verify_google_token(input_dto.token)
        email = payload.get("email")
        if not email:
            raise ValueError("Google token did not contain an email address.")

        user = self._user_repository.get_by_email(email)
        if user is None:
            # Create user in Django
            from identity.infrastructure.models import CustomUserModel, RoleModel
            from identity.application.dtos import DEFAULT_USER_AVATAR
            
            # Using email as username base to keep it simple
            username = email.split("@")[0]
            
            user_model = CustomUserModel.objects.create_user(
                email=email,
                username=username,
                password=None,  # No password for Google users
                avatar=payload.get("picture", DEFAULT_USER_AVATAR),
                auth_provider="google"
            )
            
            # They should be 'free_user' with FREE sub initially
            role = self._role_repository.get_by_name("free_user")
            if role:
                role_model = RoleModel.objects.get(id=role.id)
                user_model.roles.add(role_model)
                
            if self._create_free_subscription:
                from billing.application.dtos import CreateFreeSubscriptionForUserInputDTO
                free_sub_dto = CreateFreeSubscriptionForUserInputDTO(user_id=user_model.id)
                self._create_free_subscription.execute(free_sub_dto)
            
            from identity.infrastructure.mappers import UserMapper
            refreshed = CustomUserModel.objects.prefetch_related("roles__permissions").get(id=user_model.id)
            user = UserMapper.to_domain(refreshed)

        return _user_to_dto(user)
