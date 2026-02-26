import uuid
from typing import List, Optional, Type
from store.tips.domain.entities import Tip
from store.tips.domain.interfaces import TipRepository
from store.tips.infrastructure.models import TipModel
from store.tips.infrastructure.mappers import TipMapper
from core.infrastructure.django.repositories import DjangoBaseRepository
from django.core.cache import cache

class DjangoTipRepository(DjangoBaseRepository[Tip, TipModel], TipRepository):
    """
    Django implementation of the TipRepository.
    """
    
    @property
    def model_class(self) -> Type[TipModel]:
        return TipModel

    def _to_db_defaults(self, entity: Tip) -> dict:
        return {
            "title": entity.title,
            "description": entity.description,
            "icon": entity.icon,
            "created_at": entity.created_at
        }

    def _to_domain_entity(self, model_instance: TipModel) -> Tip:
        return TipMapper.to_domain(model_instance)

    def get_all(self) -> List[Tip]:
        models = self.model_class.objects.all()
        return [self._to_domain_entity(m) for m in models]

    def get_random(self) -> Optional[Tip]:
        last_tip_id = cache.get('last_random_tip_id')
        
        qs = self.model_class.objects.all()
        if last_tip_id:
            qs = qs.exclude(id=last_tip_id)
            
        model = qs.order_by('?').first()
        if not model:
            # Fallback if DB is empty or only has 1 tip that was just excluded
            model = self.model_class.objects.order_by('?').first()
            
        if model:
            cache.set('last_random_tip_id', str(model.id), timeout=86400) # Cache for 1 day
            return self._to_domain_entity(model)
            
        return None
