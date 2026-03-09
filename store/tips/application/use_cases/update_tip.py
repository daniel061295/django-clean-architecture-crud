from store.tips.domain.entities import Tip
from store.tips.domain.interfaces import TipRepository
from store.tips.application.dtos import UpdateTipInputDTO, TipOutputDTO
from injector import inject

class UpdateTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self, input_dto: UpdateTipInputDTO) -> TipOutputDTO:
        tip = self._repository.get_by_id(input_dto.id)
        if not tip:
            raise ValueError(f"Tip with ID {input_dto.id} not found.")
            
        # Update fields if provided
        updated_tip = Tip(
            id=tip.id,
            created_at=tip.created_at,
            title=input_dto.title if input_dto.title is not None else tip.title,
            description=input_dto.description if input_dto.description is not None else tip.description,
            icon=input_dto.icon if input_dto.icon is not None else tip.icon
        )
        
        saved_tip = self._repository.save(updated_tip)
        
        return TipOutputDTO(
            id=str(saved_tip.id),
            title=saved_tip.title,
            description=saved_tip.description,
            icon=saved_tip.icon,
            created_at=str(saved_tip.created_at)
        )
