from injector import inject

from identity.application.dtos import GetUserProfileInputDTO, UserProfileOutputDTO
from identity.domain.exceptions import UserNotFoundError
from identity.domain.interfaces import UserRepository
from core.domain.services import StorageServiceInterface
from ._helpers import _role_to_dto

class GetUserProfile:
    """Returns the full profile of a user including avatar, roles, and permissions."""

    @inject
    def __init__(self, repository: UserRepository, storage_service: StorageServiceInterface) -> None:
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: GetUserProfileInputDTO) -> UserProfileOutputDTO:
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        permission_codes = list({p.code for role in user.roles for p in role.permissions})
        
        avatar_url = user.avatar
        if (
            avatar_url 
            and not avatar_url.startswith("data:image") 
            and not avatar_url.startswith("http") 
            and avatar_url != ""
        ):
            # Generate Signed URL for R2 objects
            avatar_url = self._storage_service.get_signed_url(user.avatar) or user.avatar

        return UserProfileOutputDTO(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            avatar=avatar_url,
            roles=[_role_to_dto(r) for r in user.roles],
            permissions=permission_codes,
        )
