from typing import List, Optional, Tuple, Dict, Type
from uuid import UUID
from django.db import models
from store.provider.domain.entities import Provider
from store.provider.domain.repositories import ProviderRepository
from store.provider.infrastructure.models import ProviderModel
from store.provider.infrastructure.mappers import ProviderMapper
from core.infrastructure.django.repositories import DjangoBaseRepository

class DjangoProviderRepository(DjangoBaseRepository[Provider, ProviderModel], ProviderRepository):
    """
    Django implementation of the ProviderRepository interface.
    """

    @property
    def model_class(self) -> Type[ProviderModel]:
        return ProviderModel

    def _to_db_defaults(self, entity: Provider) -> dict:
        return {
            "name": entity.name,
            "phone": entity.phone,
            "email": entity.email,
            "address": entity.address,
            "active": entity.active,
            "updated_at": entity.updated_at,
            "created_at": entity.created_at
        }

    def _to_domain_entity(self, model_instance: ProviderModel) -> Provider:
        return ProviderMapper.to_domain(model_instance)

    def _apply_filters(self, queryset: models.QuerySet, filters: dict) -> models.QuerySet:
        queryset = queryset.order_by("-created_at")
        if filters.get("name"):
             queryset = queryset.filter(name__icontains=filters["name"])
        if filters.get("active") is not None:
            queryset = queryset.filter(active=filters["active"])
        return queryset

    def exists_by_name(self, name: str) -> bool:
        return self.model_class.objects.filter(name=name).exists()
