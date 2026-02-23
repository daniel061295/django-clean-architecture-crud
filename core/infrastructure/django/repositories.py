from typing import Any, List, Optional, Tuple, TypeVar, Generic, Type
from abc import ABC, abstractmethod
from django.db import models
from core.domain.repositories import BaseRepository

T = TypeVar('T')
M = TypeVar('M', bound=models.Model)

class DjangoBaseRepository(BaseRepository[T], ABC, Generic[T, M]):
    """
    Base Repository for Django ORM (Clean Architecture - Infrastructure Layer).
    
    This class implements the BaseRepository interface by encapsulating Django ORM interactions.
    Concrete repositories must inherit from this class and implement the mapping
    methods `_to_db_defaults` and `_to_domain_entity`, and provide the model class.
    """
    
    @property
    @abstractmethod
    def model_class(self) -> Type[M]:
        """Returns the Django Model class associated with this repository."""
        pass

    @abstractmethod
    def _to_db_defaults(self, entity: T) -> dict:
        """
        Converts a domain entity into a dictionary of fields for create/update.
        This dict is used as the 'defaults' in update_or_create.
        """
        pass

    @abstractmethod
    def _to_domain_entity(self, model_instance: M) -> T:
        """Converts a Django model instance into a domain entity."""
        pass

    def _get_pk_name(self) -> str:
        """Returns the name of the primary key field. Defaults to 'id'."""
        return "id"

    def _get_pk_value(self, entity: T) -> Any:
        """Returns the primary key value from the domain entity."""
        return getattr(entity, self._get_pk_name())

    def save(self, entity: T) -> T:
        """
        Saves or updates an entity using Django's update_or_create.
        """
        defaults = self._to_db_defaults(entity)
        pk_val = self._get_pk_value(entity)
        
        lookup_kwargs = {self._get_pk_name(): pk_val}
        
        model_instance, _ = self.model_class.objects.update_or_create(
            defaults=defaults,
            **lookup_kwargs
        )
        return self._to_domain_entity(model_instance)

    def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Retrieves an entity by its unique identifier.
        """
        lookup_kwargs = {self._get_pk_name(): entity_id}
        try:
            model_instance = self.model_class.objects.get(**lookup_kwargs)
            return self._to_domain_entity(model_instance)
        except self.model_class.DoesNotExist:
            return None

    def delete(self, entity_id: Any) -> None:
        """
        Deletes an entity by its unique identifier.
        """
        lookup_kwargs = {self._get_pk_name(): entity_id}
        self.model_class.objects.filter(**lookup_kwargs).delete()

    def _apply_filters(self, queryset: models.QuerySet, filters: dict) -> models.QuerySet:
        """
        Applies custom filters to the queryset.
        Can be overridden by child classes for complex filtering.
        """
        return queryset

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[T], int]:
        """
        Lists entities with pagination and optional filtering.
        """
        queryset = self.model_class.objects.all()
        if filters:
            queryset = self._apply_filters(queryset, filters)
            
        total_count = queryset.count()
        start = (page - 1) * page_size
        end = start + page_size
        
        items = [self._to_domain_entity(model) for model in queryset[start:end]]
        return items, total_count
