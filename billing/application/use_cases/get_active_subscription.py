import uuid
from injector import inject

from billing.application.dtos import SubscriptionOutputDTO
from billing.domain.interfaces import PlanRepository, SubscriptionRepository

class GetActiveSubscription:
    @inject
    def __init__(self, plan_repository: PlanRepository, subscription_repository: SubscriptionRepository) -> None:
        self._plan_repository = plan_repository
        self._subscription_repository = subscription_repository

    def execute(self, user_id: uuid.UUID) -> SubscriptionOutputDTO:
        subscription = self._subscription_repository.get_active_by_user(user_id)
        if subscription is None:
            raise ValueError(f"No active subscription found for user {user_id}")
            
        plan = self._plan_repository.get_by_id(subscription.plan_id)
        if plan is None:
            raise ValueError(f"Plan {subscription.plan_id} not found")
            
        return SubscriptionOutputDTO(
            id=str(subscription.id),
            user_id=str(subscription.user_id),
            plan_id=str(subscription.plan_id),
            plan_name=plan.name,
            start_date=subscription.start_date,
            end_date=subscription.end_date,
            is_active=subscription.is_active
        )
