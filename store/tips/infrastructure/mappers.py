from store.tips.domain.entities import Tip
from store.tips.infrastructure.models import TipModel

class TipMapper:
    """
    Mapper for converting between Tip domain entity and TipModel Django ORM model.
    """
    
    @staticmethod
    def to_domain(model: TipModel) -> Tip:
        return Tip(
            id=model.id,
            title=model.title,
            description=model.description,
            icon=model.icon,
            created_at=model.created_at
        )
        
    @staticmethod
    def to_model(entity: Tip) -> TipModel:
        return TipModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            icon=entity.icon,
            created_at=entity.created_at
        )
