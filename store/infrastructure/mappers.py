from store.domain.entities import PlantItem
from store.infrastructure.models import PlantItemModel

class PlantItemMapper:
    @staticmethod
    def to_domain(model: PlantItemModel) -> PlantItem:
        return PlantItem(
            id=model.id,
            name=model.name,
            description=model.description,
            price=float(model.price),
            stock=model.stock,
            created_at=model.created_at
        )

    @staticmethod
    def to_db(entity: PlantItem) -> PlantItemModel:
        return PlantItemModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            price=entity.price,
            stock=entity.stock,
            is_available=entity.is_available,
            created_at=entity.created_at
        )
