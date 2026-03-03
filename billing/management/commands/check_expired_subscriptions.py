"""
Django management command to check and handle expired PRO subscriptions.

When a PRO subscription expires:
1. Marks the PRO subscription as CANCELED
2. Automatically creates a new FREE subscription (permanent, no expiration)

This command should be run periodically (e.g., daily via cron job).
"""
from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from billing.domain.value_objects import SubscriptionStatus
from billing.infrastructure.models import PlanModel, SubscriptionModel


class Command(BaseCommand):
    """Command to check and handle expired PRO subscriptions."""

    help = "Check expired PRO subscriptions and revert users to FREE plan"

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Starting expired subscription check...\n")

        # Get FREE plan for reassignment
        try:
            free_plan = PlanModel.objects.get(name="FREE")
        except PlanModel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Error: FREE plan not found. Run 'python manage.py seed_billing' first."
                )
            )
            return

        # Find expired PRO subscriptions (ACTIVE but end_date < now)
        now = timezone.now()
        expired_subs = SubscriptionModel.objects.filter(
            status__in=[SubscriptionStatus.ACTIVE.value, SubscriptionStatus.TRIALING.value],
            end_date__lt=now,
            plan__name="PRO",
        ).select_related("user", "plan")

        if not expired_subs.exists():
            self.stdout.write(self.style.SUCCESS("No expired PRO subscriptions found."))
            return

        self.stdout.write(f"Found {expired_subs.count()} expired PRO subscription(s)...\n")

        # Process each expired subscription
        for sub in expired_subs:
            # 1. Mark PRO subscription as CANCELED
            sub.status = SubscriptionStatus.CANCELED.value
            sub.save(update_fields=["status"])

            # 2. Create new FREE subscription (permanent, no end_date)
            new_sub = SubscriptionModel.objects.create(
                user=sub.user,
                plan=free_plan,
                status=SubscriptionStatus.ACTIVE.value,
                start_date=now,
                end_date=None,  # FREE is permanent
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"  [REVERTED] {sub.user.email}: PRO -> FREE "
                    f"(PRO expired: {sub.end_date.date()}, FREE created: permanent)"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully processed {expired_subs.count()} expired subscription(s).\n"
                "Users have been reverted to FREE plan (permanent, no expiration)."
            )
        )
