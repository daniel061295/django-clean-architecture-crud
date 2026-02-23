from typing import List, Optional, Tuple, Type
from uuid import UUID
from django.db import transaction, models
from store.sale.domain.entities import Sale
from store.sale.domain.repositories import SaleRepository
from store.sale.infrastructure.models import SaleModel, SaleDetailModel
from store.sale.infrastructure.mappers import SaleMapper
from core.infrastructure.django.repositories import DjangoBaseRepository

class DjangoSaleRepository(DjangoBaseRepository[Sale, SaleModel], SaleRepository):
    """
    Django implementation of the SaleRepository interface.
    """

    @property
    def model_class(self) -> Type[SaleModel]:
        return SaleModel

    def _to_db_defaults(self, entity: Sale) -> dict:
        return {
            "date": entity.date,
            "total": entity.total,
            "status": entity.status.value,
            "created_at": entity.created_at
        }

    def _to_domain_entity(self, model_instance: SaleModel) -> Sale:
        return SaleMapper.to_domain(model_instance)

    def _apply_filters(self, queryset: models.QuerySet, filters: dict) -> models.QuerySet:
        queryset = queryset.prefetch_related('details').order_by("-created_at")
        if filters.get("status"):
            queryset = queryset.filter(status=filters["status"])
        return queryset

    def save(self, sale: Sale) -> Sale:
        """
        Custom save method for Sale that handles setting up details.
        It overrides the base generic `save()` to include `transaction.atomic()`
        and `SaleDetailModel` processing.
        """
        with transaction.atomic():
            # Let the base class save the Sale itself
            sale_domain = super().save(sale)
            
            # Now we must retrieve the saved Sale model to attach the details
            sale_model = SaleModel.objects.get(id=sale_domain.id)

            # Identify existing IDs in DB
            existing_ids = set(SaleDetailModel.objects.filter(sale=sale_model).values_list('id', flat=True))
            current_ids = {d.id for d in sale.details}
            
            # Delete removed details
            to_delete = existing_ids - current_ids
            if to_delete:
                SaleDetailModel.objects.filter(id__in=to_delete).delete()
            
            # Save/Update current details
            for detail in sale.details:
                SaleDetailModel.objects.update_or_create(
                    id=detail.id,
                    defaults={
                        "sale": sale_model,
                        "plant_item_id": detail.plant_item_id,
                        "quantity": detail.quantity,
                        "unit_price": detail.unit_price,
                        "subtotal": detail.subtotal
                    }
                )

            # It's better to fetch and convert it again using the base getter
            return self.get_by_id(sale.id)

    def get_by_id(self, sale_id: UUID) -> Optional[Sale]:
        """
        Custom get method to prefetch_related for Sale.
        """
        try:
            model = self.model_class.objects.prefetch_related('details').get(id=sale_id)
            return self._to_domain_entity(model)
        except self.model_class.DoesNotExist:
            return None
