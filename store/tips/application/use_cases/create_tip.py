from store.tips.domain.entities import Tip
from store.tips.domain.interfaces import TipRepository
from store.tips.application.dtos import CreateTipInputDTO, TipOutputDTO
from injector import inject

class CreateTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self, input_dto: CreateTipInputDTO) -> TipOutputDTO:
        tip = Tip(
            title=input_dto.title,
            description=input_dto.description,
            icon=input_dto.icon
        )
        saved_tip = self._repository.save(tip)
        return self._to_output_dto(saved_tip)
        
    def _to_output_dto(self, tip: Tip) -> TipOutputDTO:
        return TipOutputDTO(
            id=str(tip.id),
            title=tip.title,
            description=tip.description,
            icon=tip.icon,
            created_at=str(tip.created_at)
        )
