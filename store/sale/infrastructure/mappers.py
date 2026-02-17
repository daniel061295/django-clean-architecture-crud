from store.sale.domain.entities import Sale, SaleDetail, SaleStatus
from store.sale.infrastructure.models import SaleModel, SaleDetailModel

class SaleMapper:
    """
    Mapper between Sale domain entity and SaleModel Django model.
    """

    @staticmethod
    def to_domain(model: SaleModel) -> Sale:
        details = [
            SaleDetail(
                id=d.id,
                sale_id=d.sale.id,
                plant_item_id=d.plant_item_id,
                quantity=d.quantity,
                unit_price=d.unit_price,
                subtotal=d.subtotal
            )
            for d in model.details.all()
        ]
        
        return Sale(
            id=model.id,
            date=model.date,
            total=model.total,
            status=SaleStatus(model.status),
            created_at=model.created_at,
            details=details
        )

    @staticmethod
    def to_db(entity: Sale) -> SaleModel:
        return SaleModel(
            id=entity.id,
            date=entity.date,
            total=entity.total,
            status=entity.status.value,
            created_at=entity.created_at
        )
    
    @staticmethod
    def detail_to_db(detail: SaleDetail, sale_model: SaleModel) -> SaleDetailModel:
        return SaleDetailModel(
            id=detail.id,
            sale=sale_model,
            plant_item_id=detail.plant_item_id,
            quantity=detail.quantity,
            unit_price=detail.unit_price,
            subtotal=detail.subtotal
        )
