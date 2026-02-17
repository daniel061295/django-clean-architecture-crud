from uuid import UUID
from typing import Optional
from store.category.domain.repositories import CategoryRepository
from store.category.application.dtos import CategoryResponseDTO

class GetCategory:
    """
    Use case for retrieving a single Category.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, category_id: UUID) -> Optional[CategoryResponseDTO]:
        category = self.repository.get_by_id(category_id)
        if not category:
            return None
            
        return CategoryResponseDTO(
            id=category.id,
            name=category.name,
            description=category.description,
            active=category.active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
