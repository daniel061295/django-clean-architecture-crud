from uuid import UUID
from injector import inject

from identity.application.dtos import CreateUserInputDTO, UserOutputDTO
from identity.domain.exceptions import RoleNotFoundError, UserAlreadyExistsError
from identity.domain.interfaces import RoleRepository, UserRepository
from billing.application.use_cases import AssignProSubscription, CreateFreeSubscriptionForNewUser
from ._helpers import _user_to_dto

class CreateUser:
    """Creates a new Django user and assigns subscription based on plan_name."""

    @inject
    def __init__(
        self,
        role_repository: RoleRepository,
        user_repository: UserRepository,
        create_free_subscription: CreateFreeSubscriptionForNewUser = None,
        assign_pro_subscription: AssignProSubscription = None,
    ) -> None:
        self._role_repository = role_repository
        self._user_repository = user_repository
        self._create_free_subscription = create_free_subscription
        self._assign_pro_subscription = assign_pro_subscription

    def execute(self, input_dto: CreateUserInputDTO) -> UserOutputDTO:
        """
        Creates a new user via Django's ORM and assigns subscription based on plan_name.
        - If plan_name="FREE" (default): Creates FREE subscription (permanent)
        - If plan_name="PRO": Creates PRO subscription (30 days)
        Assigns default avatar to the new user.

        Args:
            input_dto: User creation data with optional plan_name.

        Returns:
            UserOutputDTO: The created user.

        Raises:
            RoleNotFoundError: If any specified role name does not exist.
        """
        from identity.application.dtos import DEFAULT_USER_AVATAR
        
        # Check if email already exists
        if self._user_repository.get_by_email(input_dto.email) is not None:
            raise UserAlreadyExistsError(f"El correo {input_dto.email} ya se encuentra registrado.")

        avatar_to_use = input_dto.avatar if input_dto.avatar else DEFAULT_USER_AVATAR

        # Use Django's manager to safely hash the password
        from identity.infrastructure.models import CustomUserModel
        user_model = CustomUserModel.objects.create_user(
            email=input_dto.email,
            username=input_dto.username,
            password=input_dto.password,
            avatar=avatar_to_use,  # Set default avatar or custom
        )
        for role_name in input_dto.role_names:
            role = self._role_repository.get_by_name(role_name)
            if role is None:
                raise RoleNotFoundError(f"Role '{role_name}' does not exist.")
            from identity.infrastructure.models import RoleModel
            role_model = RoleModel.objects.get(id=role.id)
            user_model.roles.add(role_model)

        # Create subscription based on plan_name
        if input_dto.plan_name.upper() == "PRO":
            # Assign PRO subscription (cancels any existing FREE)
            if self._assign_pro_subscription is not None:
                from billing.application.use_cases import AssignProSubscription
                self._assign_pro_subscription.execute(user_model.id)
        else:
            # Create FREE subscription (permanent, default)
            if self._create_free_subscription is not None:
                from billing.application.dtos import CreateFreeSubscriptionForUserInputDTO
                free_sub_dto = CreateFreeSubscriptionForUserInputDTO(user_id=user_model.id)
                self._create_free_subscription.execute(free_sub_dto)

        # Re-fetch with relations
        from identity.infrastructure.mappers import UserMapper
        from identity.infrastructure.models import CustomUserModel as M
        refreshed = M.objects.prefetch_related("roles__permissions").get(id=user_model.id)
        return _user_to_dto(UserMapper.to_domain(refreshed))
