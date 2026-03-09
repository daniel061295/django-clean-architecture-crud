from injector import inject

from identity.application.dtos import AssignRoleToUserInputDTO, UserOutputDTO
from identity.domain.exceptions import UserNotFoundError
from identity.domain.interfaces import UserRepository
from ._helpers import _user_to_dto

class AssignRoleToUser:
    """Assigns a role to an existing user."""

    @inject
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: AssignRoleToUserInputDTO) -> UserOutputDTO:
        """
        Assigns a role to a user.

        Args:
            input_dto: User UUID and Role UUID.

        Returns:
            UserOutputDTO: The updated user.

        Raises:
            UserNotFoundError: If the user does not exist.
        """
        if self._repository.get_by_id(input_dto.user_id) is None:
            raise UserNotFoundError(f"User '{input_dto.user_id}' not found.")

        updated = self._repository.assign_role(input_dto.user_id, input_dto.role_id)
        return _user_to_dto(updated)
