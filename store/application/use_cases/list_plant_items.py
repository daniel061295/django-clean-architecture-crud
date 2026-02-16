from typing import Tuple, List
from store.domain.repositories import PlantItemRepository
from store.application.dtos import ListPlantItemsQueryDTO, PaginatedPlantItemsDTO, PlantItemResponseDTO

class ListPlantItems:
    def __init__(self, repository: PlantItemRepository):
        self.repository = repository

    def execute(self, query: ListPlantItemsQueryDTO) -> PaginatedPlantItemsDTO:
        filters = {
            'min_price': query.min_price,
            'max_price': query.max_price,
            'is_available': query.is_available,
            'name_contains': query.name_contains
        }
        
        # Repository returns (items, total_count)
        items, total_count = self.repository.list(
            page=query.page,
            page_size=query.page_size,
            filters=filters
        )
        
        response_items = [
            PlantItemResponseDTO(
                id=item.id,
                name=item.name,
                description=item.description,
                price=item.price,
                stock=item.stock,
                is_available=item.is_available,
                created_at=item.created_at
            ) for item in items
        ]
        
        total_pages = (total_count + query.page_size - 1) // query.page_size
        
        return PaginatedPlantItemsDTO(
            items=response_items,
            page=query.page,
            page_size=query.page_size,
            total_count=total_count,
            total_pages=total_pages
        )
