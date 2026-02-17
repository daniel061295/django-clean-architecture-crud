from store.plant_item.domain.entities import PlantItem
from store.plant_item.infrastructure.models import PlantItemModel


class PlantItemMapper:
    """
    Mapper for converting between Domain Entities and Django Models.
    """

    @staticmethod
    def to_domain(model: PlantItemModel) -> PlantItem:
        """
        Converts a Django model instance to a Domain entity.
        """
        return PlantItem(
            id=model.id,
            name=model.name,
            description=model.description,
            price=float(model.price),
            stock=model.stock,
            created_at=model.created_at,
        )

    @staticmethod
    def to_db(entity: PlantItem) -> PlantItemModel:
        """
        Converts a Domain entity to a Django model instance (unsaved).
        """
        return PlantItemModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            price=entity.price,
            stock=entity.stock,
            is_available=entity.is_available,
            created_at=entity.created_at,
        )
