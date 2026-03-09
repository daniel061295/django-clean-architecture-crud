from typing import List
from injector import inject

from billing.application.dtos import CreatePlanInputDTO, PlanOutputDTO
from billing.domain.entities import Plan
from billing.domain.interfaces import PlanRepository

class CreatePlan:
    @inject
    def __init__(self, repository: PlanRepository) -> None:
        self._repository = repository

    def execute(self, input_dto: CreatePlanInputDTO) -> PlanOutputDTO:
        plan = Plan(
            name=input_dto.name,
            price=input_dto.price,
            scan_limit_per_day=input_dto.scan_limit_per_day,
            features=input_dto.features,
            stripe_price_id=input_dto.stripe_price_id
        )
        saved = self._repository.save(plan)
        return PlanOutputDTO(
            id=str(saved.id),
            name=saved.name,
            price=saved.price,
            scan_limit_per_day=saved.scan_limit_per_day,
            features=saved.features,
            stripe_price_id=saved.stripe_price_id,
            is_active=saved.is_active
        )


class GetPlan:
    @inject
    def __init__(self, repository: PlanRepository) -> None:
        self._repository = repository

    def execute(self, plan_id: str) -> PlanOutputDTO:
        plan = self._repository.get_by_id(plan_id)
        if plan is None:
            raise ValueError(f"Plan {plan_id} not found")
            
        return PlanOutputDTO(
            id=str(plan.id),
            name=plan.name,
            price=plan.price,
            scan_limit_per_day=plan.scan_limit_per_day,
            features=plan.features,
            stripe_price_id=plan.stripe_price_id,
            is_active=plan.is_active
        )


class ListPlans:
    @inject
    def __init__(self, repository: PlanRepository) -> None:
        self._repository = repository

    def execute(self) -> List[PlanOutputDTO]:
        plans = self._repository.list_active()
        return [
            PlanOutputDTO(
                id=str(p.id),
                name=p.name,
                price=p.price,
                scan_limit_per_day=p.scan_limit_per_day,
                features=p.features,
                stripe_price_id=p.stripe_price_id,
                is_active=p.is_active
            ) for p in plans
        ]
