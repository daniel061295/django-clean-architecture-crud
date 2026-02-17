from uuid import UUID
from store.category.domain.repositories import CategoryRepository

class DeleteCategory:
    """
    Use case for deleting a Category.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, category_id: UUID) -> None:
        """
        Executes the delete category use case.

        Args:
            category_id: UUID of the category to delete.

        Returns:
            None
        """
        if not self.repository.get_by_id(category_id):
             raise ValueError(f"Category with id {category_id} not found.")
             
        self.repository.delete(category_id)
