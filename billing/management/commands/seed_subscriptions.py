"""
Django management command to seed subscriptions for test users.

Uses application use cases to ensure business logic is properly applied,
including automatic cancellation of FREE subscriptions when assigning PRO.
"""
from django.core.management.base import BaseCommand
from injector import Injector

from config.di import create_injector
from billing.application.use_cases import AssignProSubscription, CreateFreeSubscriptionForNewUser


class Command(BaseCommand):
    """Command to seed the database with subscriptions for test users."""

    help = "Seed the database with subscriptions for test users"

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Starting subscriptions seed...\n")

        # Initialize injector for use case dependencies
        self.injector = create_injector()

        # Get use cases
        assign_pro = self.injector.get(AssignProSubscription)
        create_free = self.injector.get(CreateFreeSubscriptionForNewUser)

        # Assign PRO subscription to admin user (daniel061295@gmail.com)
        # This will automatically cancel any existing FREE subscription
        try:
            from identity.models import CustomUserModel
            admin_user = CustomUserModel.objects.get(email="daniel061295@gmail.com")
            assign_pro.execute(admin_user.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [ASSIGNED] PRO subscription for {admin_user.email} (FREE canceled if existed)"
                )
            )
        except CustomUserModel.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    "  [SKIP] Admin user 'daniel061295@gmail.com' not found"
                )
            )

        # Assign PRO subscription to subscriber user
        try:
            subscriber_user = CustomUserModel.objects.get(email="subscriber@example.com")
            assign_pro.execute(subscriber_user.id)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [ASSIGNED] PRO subscription for {subscriber_user.email} (FREE canceled if existed)"
                )
            )
        except CustomUserModel.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    "  [SKIP] Subscriber user 'subscriber@example.com' not found"
                )
            )

        # Create FREE subscription for freeuser (permanent, no end date)
        try:
            from billing.application.dtos import CreateFreeSubscriptionForUserInputDTO
            free_user = CustomUserModel.objects.get(email="freeuser@test.com")
            input_dto = CreateFreeSubscriptionForUserInputDTO(user_id=free_user.id)
            create_free.execute(input_dto)
            self.stdout.write(
                self.style.SUCCESS(
                    f"  [ASSIGNED] FREE subscription for {free_user.email} (permanent, no expiration)"
                )
            )
        except CustomUserModel.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    "  [SKIP] Free user 'freeuser@test.com' not found"
                )
            )

        self.stdout.write(self.style.SUCCESS("\nSuccessfully seeded subscriptions!"))
        self.stdout.write(
            self.style.WARNING(
                "\nNote: PRO subscriptions expire in 30 days.\n"
                "FREE subscriptions are permanent (no expiration).\n"
                "When PRO expires, users automatically return to FREE."
            )
        )
