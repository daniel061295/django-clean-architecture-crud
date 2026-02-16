from typing import List, Optional, Tuple, Dict
from uuid import UUID
from store.domain.entities import PlantItem
from store.domain.repositories import PlantItemRepository
from store.infrastructure.models import PlantItemModel
from store.infrastructure.mappers import PlantItemMapper

class DjangoPlantItemRepository(PlantItemRepository):
    def save(self, plant_item: PlantItem) -> PlantItem:
        defaults = {
            'name': plant_item.name,
            'description': plant_item.description,
            'price': plant_item.price,
            'stock': plant_item.stock,
            'is_available': plant_item.is_available,
            'created_at': plant_item.created_at
        }
        
        model, created = PlantItemModel.objects.update_or_create(
            id=plant_item.id,
            defaults=defaults
        )
        return PlantItemMapper.to_domain(model)

    def get_by_id(self, item_id: UUID) -> Optional[PlantItem]:
        try:
            model = PlantItemModel.objects.get(id=item_id)
            return PlantItemMapper.to_domain(model)
        except PlantItemModel.DoesNotExist:
            return None

    def list(self, page: int, page_size: int, filters: Dict) -> Tuple[List[PlantItem], int]:
        queryset = PlantItemModel.objects.all()

        if filters.get('min_price') is not None:
            queryset = queryset.filter(price__gte=filters['min_price'])
        if filters.get('max_price') is not None:
            queryset = queryset.filter(price__lte=filters['max_price'])
        if filters.get('is_available') is not None:
            queryset = queryset.filter(is_available=filters['is_available'])
        if filters.get('name_contains') is not None:
            queryset = queryset.filter(name__icontains=filters['name_contains'])

        total_count = queryset.count()
        
        start = (page - 1) * page_size
        end = start + page_size
        
        items = [PlantItemMapper.to_domain(model) for model in queryset[start:end]]
        return items, total_count

    def delete(self, item_id: UUID) -> None:
        PlantItemModel.objects.filter(id=item_id).delete()

    def exists(self, item_id: UUID) -> bool:
        return PlantItemModel.objects.filter(id=item_id).exists()
