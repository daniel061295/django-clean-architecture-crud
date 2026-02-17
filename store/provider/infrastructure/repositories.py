from typing import List, Optional, Tuple, Dict
from uuid import UUID
from store.provider.domain.entities import Provider
from store.provider.domain.repositories import ProviderRepository
from store.provider.infrastructure.models import ProviderModel
from store.provider.infrastructure.mappers import ProviderMapper
from django.core.paginator import Paginator

class DjangoProviderRepository(ProviderRepository):
    """
    Django implementation of the ProviderRepository interface.
    """

    def save(self, provider: Provider) -> Provider:
        model, created = ProviderModel.objects.update_or_create(
            id=provider.id,
            defaults={
                "name": provider.name,
                "phone": provider.phone,
                "email": provider.email,
                "address": provider.address,
                "active": provider.active,
                "updated_at": provider.updated_at,
                "created_at": provider.created_at
            }
        )
        return ProviderMapper.to_domain(model)

    def get_by_id(self, provider_id: UUID) -> Optional[Provider]:
        try:
            model = ProviderModel.objects.get(id=provider_id)
            return ProviderMapper.to_domain(model)
        except ProviderModel.DoesNotExist:
            return None

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Provider], int]:
        queryset = ProviderModel.objects.all().order_by("-created_at")

        if filters.get("name"):
             queryset = queryset.filter(name__icontains=filters["name"])
        
        if filters.get("active") is not None:
            queryset = queryset.filter(active=filters["active"])

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return [ProviderMapper.to_domain(item) for item in page_obj], paginator.count

    def delete(self, provider_id: UUID) -> None:
        ProviderModel.objects.filter(id=provider_id).delete()
        
    def exists_by_name(self, name: str) -> bool:
        return ProviderModel.objects.filter(name=name).exists()
