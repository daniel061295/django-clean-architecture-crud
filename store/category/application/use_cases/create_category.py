from store.category.domain.entities import Category
from store.category.domain.repositories import CategoryRepository
from store.category.application.dtos import CreateCategoryDTO, CategoryResponseDTO

class CreateCategory:
    """
    Use case for creating a new Category.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, dto: CreateCategoryDTO) -> CategoryResponseDTO:
        if self.repository.exists_by_name(dto.name):
            raise ValueError(f"Category with name '{dto.name}' already exists.")

        category = Category.create(
            name=dto.name,
            description=dto.description
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
