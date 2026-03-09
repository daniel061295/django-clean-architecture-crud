from datetime import date
import uuid
from injector import inject

from billing.application.dtos import CreateFreeSubscriptionForUserInputDTO, SubscriptionOutputDTO
from billing.domain.entities import Subscription
from billing.domain.interfaces import PlanRepository, SubscriptionRepository

class CreateFreeSubscriptionForNewUser:
    """Creates a 'FREE' subscription for a newly registered user."""
    
    @inject
    def __init__(self, plan_repository: PlanRepository, subscription_repository: SubscriptionRepository) -> None:
        self._plan_repository = plan_repository
        self._subscription_repository = subscription_repository

    def execute(self, input_dto: CreateFreeSubscriptionForUserInputDTO) -> SubscriptionOutputDTO:
        free_plan = self._plan_repository.get_by_name("FREE")
        if free_plan is None:
            raise ValueError("FREE plan not configured in the system.")
            
        # Optional: Check if user already has an active subscription
        active_sub = self._subscription_repository.get_active_by_user(input_dto.user_id)
        if active_sub:
            if str(active_sub.plan_id) == str(free_plan.id):
                # Already has FREE plan
                return SubscriptionOutputDTO(
                    id=str(active_sub.id),
                    user_id=str(active_sub.user_id),
                    plan_id=str(active_sub.plan_id),
                    plan_name=free_plan.name,
                    start_date=active_sub.start_date,
                    end_date=active_sub.end_date,
                    is_active=active_sub.is_active
                )
            else:
                raise ValueError("User already has an active subscription.")

        subscription = Subscription(
            user_id=input_dto.user_id,
            plan_id=free_plan.id,
            start_date=date.today(),
            end_date=None,  # Free is permanent unless upgraded
            is_active=True
        )
        
        saved = self._subscription_repository.save(subscription)
        
        return SubscriptionOutputDTO(
            id=str(saved.id),
            user_id=str(saved.user_id),
            plan_id=str(saved.plan_id),
            plan_name=free_plan.name,
            start_date=saved.start_date,
            end_date=saved.end_date,
            is_active=saved.is_active
        )
