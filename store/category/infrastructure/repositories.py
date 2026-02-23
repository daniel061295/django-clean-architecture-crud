from typing import List, Optional, Tuple, Type
from uuid import UUID
from datetime import datetime
from django.db import models
from store.category.domain.entities import Category
from store.category.domain.repositories import CategoryRepository
from store.category.infrastructure.models import CategoryModel
from store.category.infrastructure.mappers import CategoryMapper
from core.infrastructure.django.repositories import DjangoBaseRepository
from core.infrastructure.dynamodb.repositories import DynamoDBBaseRepository

class DjangoCategoryRepository(DjangoBaseRepository[Category, CategoryModel], CategoryRepository):
    """
    Django implementation of the CategoryRepository interface.
    """

    @property
    def model_class(self) -> Type[CategoryModel]:
        return CategoryModel

    def _to_db_defaults(self, entity: Category) -> dict:
        return {
            "name": entity.name,
            "description": entity.description,
            "active": entity.active,
            "updated_at": entity.updated_at,
            "created_at": entity.created_at
        }

    def _to_domain_entity(self, model_instance: CategoryModel) -> Category:
        return CategoryMapper.to_domain(model_instance)

    def _apply_filters(self, queryset: models.QuerySet, filters: dict) -> models.QuerySet:
        queryset = queryset.order_by("-created_at")
        if filters.get("name"):
            queryset = queryset.filter(name__icontains=filters["name"])
        if filters.get("active") is not None:
            queryset = queryset.filter(active=filters["active"])
        return queryset
        
    def exists_by_name(self, name: str) -> bool:
        """
        Checks if a Category domain entity with the given name exists.
        """
        return self.model_class.objects.filter(name=name).exists()

class DynamoDBCategoryRepository(DynamoDBBaseRepository[Category], CategoryRepository):
    """
    DynamoDB implementation of the CategoryRepository interface.
    """
    def __init__(self):
        super().__init__(
            table_name="categories",
            pk_name="id",
            sk_name=None
        )

    def _to_db_dict(self, entity: Category) -> dict:
        return {
            "id": str(entity.id),
            "name": entity.name,
            "description": entity.description,
            "active": entity.active,
            "updated_at": entity.updated_at.isoformat() if entity.updated_at else None,
            "created_at": entity.created_at.isoformat() if entity.created_at else None
        }

    def _to_domain_entity(self, item_dict: dict) -> Category:
        return Category(
            id=UUID(item_dict["id"]),
            name=item_dict["name"],
            description=item_dict.get("description"),
            active=item_dict.get("active", True),
            created_at=datetime.fromisoformat(item_dict["created_at"]) if item_dict.get("created_at") else None,
            updated_at=datetime.fromisoformat(item_dict["updated_at"]) if item_dict.get("updated_at") else None
        )
    
    def exists_by_name(self, name: str) -> bool:
        """
        Checks if a Category domain entity with the given name exists.
        """
        return self._exists_by_attribute('name', name)