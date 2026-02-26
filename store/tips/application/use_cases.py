from store.tips.domain.entities import Tip
from store.tips.domain.interfaces import TipRepository
from store.tips.application.dtos import CreateTipInputDTO, UpdateTipInputDTO, TipOutputDTO
from typing import List
from injector import inject
import uuid

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

class GetTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self, tip_id: uuid.UUID) -> TipOutputDTO:
        tip = self._repository.get_by_id(tip_id)
        if not tip:
            raise ValueError(f"Tip with ID {tip_id} not found.")
            
        return TipOutputDTO(
            id=str(tip.id),
            title=tip.title,
            description=tip.description,
            icon=tip.icon,
            created_at=str(tip.created_at)
        )

class GetRandomTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self) -> TipOutputDTO:
        tip = self._repository.get_random()
        if not tip:
            raise ValueError("No tips available.")
            
        return TipOutputDTO(
            id=str(tip.id),
            title=tip.title,
            description=tip.description,
            icon=tip.icon,
            created_at=str(tip.created_at)
        )

class GetAllTipsUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self) -> List[TipOutputDTO]:
        tips = self._repository.get_all()
        return [
            TipOutputDTO(
                id=str(t.id),
                title=t.title,
                description=t.description,
                icon=t.icon,
                created_at=str(t.created_at)
            ) for t in tips
        ]

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

class DeleteTipUseCase:
    @inject
    def __init__(self, repository: TipRepository):
        self._repository = repository

    def execute(self, tip_id: uuid.UUID) -> None:
        success = self._repository.delete(tip_id)
        if not success:
            raise ValueError(f"Tip with ID {tip_id} not found.")
