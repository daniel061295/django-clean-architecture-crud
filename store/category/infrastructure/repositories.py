from typing import List, Optional, Tuple
from uuid import UUID
from django.core.paginator import Paginator
from store.category.domain.entities import Category
from store.category.domain.repositories import CategoryRepository
from store.category.infrastructure.models import CategoryModel
from store.category.infrastructure.mappers import CategoryMapper

class DjangoCategoryRepository(CategoryRepository):
    """
    Django implementation of the CategoryRepository interface.
    """

    def save(self, category: Category) -> Category:
        """
        Saves a Category domain entity to the database.

        Args:
            category: Category domain entity to save.

        Returns:
            Category domain entity.
        """
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
        """
        Retrieves a Category domain entity by its ID.

        Args:
            category_id: UUID of the category to retrieve.

        Returns:
            Category domain entity or None if not found.
        """
        try:
            model = CategoryModel.objects.get(id=category_id)
            return CategoryMapper.to_domain(model)
        except CategoryModel.DoesNotExist:
            return None

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Category], int]:
        """
        Lists Category domain entities with pagination and filters.

        Args:
            page: Page number.
            page_size: Number of categories per page.
            filters: Dictionary of filters to apply.

        Returns:
            Tuple of list of Category domain entities and total count.
        """
        queryset = CategoryModel.objects.all().order_by("-created_at")

        if filters.get("name"):
             queryset = queryset.filter(name__icontains=filters["name"])
        
        if filters.get("active") is not None:
            queryset = queryset.filter(active=filters["active"])

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return [CategoryMapper.to_domain(item) for item in page_obj], paginator.count

    def delete(self, category_id: UUID) -> None:
        """
        Deletes a Category domain entity by its ID.

        Args:
            category_id: UUID of the category to delete.

        Returns:
            None
        """
        CategoryModel.objects.filter(id=category_id).delete()
        
    def exists_by_name(self, name: str) -> bool:
        """
        Checks if a Category domain entity with the given name exists.

        Args:
            name: Name of the category to check.

        Returns:
            True if category exists, False otherwise.
        """
        return CategoryModel.objects.filter(name=name).exists()
