from store.history.domain.interfaces import HistoryRepository
from store.history.domain.entities import History
from store.history.infrastructure.models import HistoryModel
from store.history.infrastructure.mappers import HistoryMapper
from typing import Optional, List

class DjangoHistoryRepository(HistoryRepository):
    """
    Django implementation of the HistoryRepository interface.
    """
    def save(self, history: History) -> History:
        model = HistoryMapper.to_db(history)
        model.save()
        return HistoryMapper.to_domain(model)

    def get_by_id(self, history_id: str) -> Optional[History]:
        try:
            model = HistoryModel.objects.get(id=history_id)
            return HistoryMapper.to_domain(model)
        except HistoryModel.DoesNotExist:
            return None

    def get_all(self) -> List[History]:
        models = HistoryModel.objects.all().order_by('-created_at')
        return [HistoryMapper.to_domain(model) for model in models]

    def get_by_user_id(self, user_id: str) -> List[History]:
        models = HistoryModel.objects.filter(user_id=user_id).order_by('-created_at')
        return [HistoryMapper.to_domain(model) for model in models]

    def delete(self, history_id: str) -> bool:
        try:
            model = HistoryModel.objects.get(id=history_id)
            model.delete()
            return True
        except HistoryModel.DoesNotExist:
            return False

    def delete_all(self) -> None:
        HistoryModel.objects.all().delete()
