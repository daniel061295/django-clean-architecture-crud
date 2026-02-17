from typing import Tuple, List
from store.plant_item.domain.repositories import PlantItemRepository
from store.plant_item.application.dtos import (
    ListPlantItemsQueryDTO,
    PaginatedPlantItemsDTO,
    PlantItemResponseDTO,
)


class ListPlantItems:
    """
    Use case for listing PlantItems with pagination and filtering.
    """

    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, query: ListPlantItemsQueryDTO) -> PaginatedPlantItemsDTO:
        """
        Executes the list query.

        Args:
            query (ListPlantItemsQueryDTO): Query parameters.

        Returns:
            PaginatedPlantItemsDTO: Paginated results.
        """
        filters = {
            "min_price": query.min_price,
            "max_price": query.max_price,
            "is_available": query.is_available,
            "name_contains": query.name_contains,
        }

        # Repository returns (items, total_count)
        items, total_count = self.repository.list(
            page=query.page, page_size=query.page_size, filters=filters
        )

        response_items = [
            PlantItemResponseDTO(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                stock=item.stock,
                is_available=item.is_available,
                created_at=item.created_at,
            )
            for item in items
        ]

        total_pages = (total_count + query.page_size - 1) // query.page_size

        return PaginatedPlantItemsDTO(
            items=response_items,
            page=query.page,
            page_size=query.page_size,
            total_count=total_count,
            total_pages=total_pages,
        )
