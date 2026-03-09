from uuid import UUID
from injector import inject

from identity.application.dtos import UserOutputDTO
from identity.domain.exceptions import UserNotFoundError
from identity.domain.interfaces import UserRepository
from ._helpers import _user_to_dto

class GetUser:
    """Retrieves a single user by UUID."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, user_id: UUID) -> UserOutputDTO:
        """
        Fetches a user by UUID.

        Args:
            user_id: The UUID of the user.

        Returns:
            UserOutputDTO: The user data.

        Raises:
            UserNotFoundError: If no user with this UUID exists.
        """
        user = self._repository.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User '{user_id}' not found.")
        return _user_to_dto(user)
