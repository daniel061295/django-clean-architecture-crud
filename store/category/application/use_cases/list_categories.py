from typing import List, Tuple
from store.category.domain.repositories import CategoryRepository
from store.category.application.dtos import CategoryResponseDTO

class ListCategories:
    """
    Use case for listing Categories.
    """

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    def execute(self, page: int, 
                page_size: int, 
                filters: dict) -> Tuple[List[CategoryResponseDTO], int]:
        """
        Executes the list categories use case.

        Args:
            page: Page number.
            page_size: Number of categories per page.
            filters: Filters to apply to the categories.

        Returns:
            Tuple of list of CategoryResponseDTO and total count.
        """
        categories, total_count = self.repository.list(page, page_size, filters)
        
        dtos = [
            CategoryResponseDTO(
                id=c.id,
                name=c.name,
                description=c.description,
                active=c.active,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in categories
        ]
        
        return dtos, total_count
