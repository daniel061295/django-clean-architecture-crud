from typing import List, Optional, Tuple
from uuid import UUID
from django.core.paginator import Paginator
from django.db import transaction
from store.sale.domain.entities import Sale
from store.sale.domain.repositories import SaleRepository
from store.sale.infrastructure.models import SaleModel, SaleDetailModel
from store.sale.infrastructure.mappers import SaleMapper

class DjangoSaleRepository(SaleRepository):
    """
    Django implementation of the SaleRepository interface.
    """

    def save(self, sale: Sale) -> Sale:
        with transaction.atomic():
            sale_model, created = SaleModel.objects.update_or_create(
                id=sale.id,
                defaults={
                    "date": sale.date,
                    "total": sale.total,
                    "status": sale.status.value,
                    "created_at": sale.created_at
                }
            )

            # Identify existing IDs in DB
            existing_ids = set(SaleDetailModel.objects.filter(sale=sale_model).values_list('id', flat=True))
            current_ids = {d.id for d in sale.details}
            
            # Delete removed
            to_delete = existing_ids - current_ids
            if to_delete:
                SaleDetailModel.objects.filter(id__in=to_delete).delete()
            
            # Save/Update current
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

            return self.get_by_id(sale.id)

    def get_by_id(self, sale_id: UUID) -> Optional[Sale]:
        try:
            model = SaleModel.objects.prefetch_related('details').get(id=sale_id)
            return SaleMapper.to_domain(model)
        except SaleModel.DoesNotExist:
            return None

    def list(self, page: int, page_size: int, filters: dict) -> Tuple[List[Sale], int]:
        queryset = SaleModel.objects.prefetch_related('details').all().order_by("-created_at")
        
        # Add filtering logic if needed
        if filters.get("status"):
            queryset = queryset.filter(status=filters["status"])

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        return [SaleMapper.to_domain(item) for item in page_obj], paginator.count
