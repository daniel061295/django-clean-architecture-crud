from store.history.domain.entities import History
from store.history.infrastructure.models import HistoryModel

class HistoryMapper:
    """
    Maps between Domain Entity and ORM Model for History.
    """

    @staticmethod
    def to_domain(model: HistoryModel) -> History:
        return History(
            id=str(model.id),
            is_healthy=model.is_healthy,
            title=model.title,
            diagnosis=model.diagnosis,
            confidence=model.confidence,
            treatment=model.treatment,
            urgency_level=model.urgency_level,
            photo=model.photo,
            created_at=model.created_at
        )

    @staticmethod
    def to_db(entity: History) -> HistoryModel:
        return HistoryModel(
            id=entity.id,
            is_healthy=entity.is_healthy,
            title=entity.title,
            diagnosis=entity.diagnosis,
            confidence=entity.confidence,
            treatment=entity.treatment,
            urgency_level=entity.urgency_level,
            photo=entity.photo,
            created_at=entity.created_at
        )
