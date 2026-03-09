from injector import inject

from identity.application.dtos import UpdateUserAvatarInputDTO, DeleteUserAvatarInputDTO, UserAvatarOutputDTO
from identity.domain.exceptions import UserNotFoundError
from identity.domain.interfaces import UserRepository
from core.domain.services import StorageServiceInterface
from ._helpers import _validate_avatar_base64

class UpdateUserAvatar:
    """Updates a user's avatar image."""

    @inject
    def __init__(self, repository: UserRepository, storage_service: StorageServiceInterface) -> None:
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: UpdateUserAvatarInputDTO) -> UserAvatarOutputDTO:
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")
        
        # Validate the base64 avatar
        _validate_avatar_base64(input_dto.avatar_base64)

        import base64
        from core.utils.images import optimize_image

        base64_data = input_dto.avatar_base64.split(',', 1)[1]
        raw_bytes = base64.b64decode(base64_data)
        optimized_bytes = optimize_image(raw_bytes, max_size=(500, 500), quality=80)

        # Upload to R2 Storage
        file_name = f"avatars/{input_dto.user_id}.jpg"
        r2_key = self._storage_service.upload_file(optimized_bytes, file_name, "image/jpeg")

        if user.avatar and not user.avatar.startswith("data:image"):
            try:
                self._storage_service.delete_file(user.avatar)
            except Exception:
                pass

        updated_user = self._repository.update_avatar(input_dto.user_id, r2_key)
        signed_url = self._storage_service.get_signed_url(updated_user.avatar) or updated_user.avatar

        return UserAvatarOutputDTO(avatar=signed_url)


class DeleteUserAvatar:
    """Deletes a user's avatar image."""

    @inject
    def __init__(self, repository: UserRepository, storage_service: StorageServiceInterface) -> None:
        self._repository = repository
        self._storage_service = storage_service

    def execute(self, input_dto: DeleteUserAvatarInputDTO) -> UserAvatarOutputDTO:
        user = self._repository.get_by_id(input_dto.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        if user.avatar and not user.avatar.startswith("data:image"):
            try:
                self._storage_service.delete_file(user.avatar)
            except Exception:
                pass

        updated_user = self._repository.delete_avatar(input_dto.user_id)
        return UserAvatarOutputDTO(avatar=updated_user.avatar)
