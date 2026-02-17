from store.category.domain.repositories import CategoryRepository
from store.category.application.dtos import UpdateCategoryDTO, CategoryResponseDTO

class UpdateCategory:
    """
    Use case for updating a Category.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, dto: UpdateCategoryDTO) -> CategoryResponseDTO:
        """
        Executes the update category use case.

        Args:
            dto: UpdateCategoryDTO with category data.

        Returns:
            CategoryResponseDTO with updated category data.
        """
        category = self.repository.get_by_id(dto.id)
        if not category:
            raise ValueError(f"Category with id {dto.id} not found.")

        # Check unique name if name is changing
        if dto.name and dto.name != category.name:
            if self.repository.exists_by_name(dto.name):
                raise ValueError(f"Category with name '{dto.name}' already exists.")

        category.update(
            name=dto.name,
            description=dto.description,
            active=dto.active
        )
        saved_category = self.repository.save(category)

        return CategoryResponseDTO(
            id=saved_category.id,
            name=saved_category.name,
            description=saved_category.description,
            active=saved_category.active,
            created_at=saved_category.created_at,
            updated_at=saved_category.updated_at
        )
