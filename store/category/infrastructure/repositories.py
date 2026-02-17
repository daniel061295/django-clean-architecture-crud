from typing import List, Optional, Tuple, Dict
from uuid import UUID
from store.category.domain.entities import Category
from store.category.domain.repositories import CategoryRepository
from store.category.infrastructure.models import CategoryModel
from store.category.infrastructure.mappers import CategoryMapper
from django.core.paginator import Paginator

class DjangoCategoryRepository(CategoryRepository):
    """
    Django implementation of the CategoryRepository interface.
    """

    def save(self, category: Category) -> Category:
        model, created = CategoryModel.objects.update_or_create(
            id=category.id,
            defaults={
                "name": category.name,
                "description": category.description,
                "active": category.active,
                "updated_at": category.updated_at,
                "created_at": category.created_at # Ensure created_at is preserved/set
            }
        )
        return CategoryMapper.to_domain(model)

    def get_by_id(self, category_id: UUID) -> Optional[Category]:
        try:
            model = CategoryModel.objects.get(id=category_id)
            return CategoryMapper.to_domain(model)
        except CategoryModel.DoesNotExist:
            return None

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Category], int]:
        queryset = CategoryModel.objects.all().order_by("-created_at")

        if filters.get("name"):
             queryset = queryset.filter(name__icontains=filters["name"])
        
        if filters.get("active") is not None:
            queryset = queryset.filter(active=filters["active"])

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return [CategoryMapper.to_domain(item) for item in page_obj], paginator.count

    def delete(self, category_id: UUID) -> None:
        CategoryModel.objects.filter(id=category_id).delete()
        
    def exists_by_name(self, name: str) -> bool:
        return CategoryModel.objects.filter(name=name).exists()
