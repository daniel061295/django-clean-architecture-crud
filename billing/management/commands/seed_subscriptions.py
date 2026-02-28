"""
Django management command to seed subscriptions for test users.
"""
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from billing.models import PlanModel, SubscriptionModel
from identity.models import CustomUserModel


class Command(BaseCommand):
    """Command to seed the database with subscriptions for test users."""

    help = "Seed the database with subscriptions for test users"

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Starting subscriptions seed...\n")

        # Get plans
        try:
            free_plan = PlanModel.objects.get(name="FREE")
            pro_plan = PlanModel.objects.get(name="PRO")
        except PlanModel.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    "Error: Plans not found. Run 'python manage.py seed_billing' first."
                )
            )
            return

        # Get users
        try:
            admin_user = CustomUserModel.objects.get(email="daniel061295@gmail.com")
            subscriber_user = CustomUserModel.objects.get(email="subscriber@test.com")
            free_user = CustomUserModel.objects.get(email="freeuser@test.com")
        except CustomUserModel.DoesNotExist as e:
            self.stdout.write(
                self.style.ERROR(
                    f"Error: User not found. Run 'python manage.py seed_identity' first. ({e})"
                )
            )
            return

        # Calculate end date (1 month from now)
        start_date = timezone.now()
        end_date = start_date + timedelta(days=30)

        # Create subscription for admin user (daniel061295@gmail.com) - PRO
        admin_sub, created = SubscriptionModel.objects.update_or_create(
            user=admin_user,
            plan=pro_plan,
            defaults={
                "status": "ACTIVE",
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        status = "CREATED" if created else "UPDATED"
        self.stdout.write(
            self.style.SUCCESS(
                f"  [{status}] PRO subscription for {admin_user.email} (ends: {end_date.date()})"
            )
        )

        # Create subscription for subscriber user - PRO
        subscriber_sub, created = SubscriptionModel.objects.update_or_create(
            user=subscriber_user,
            plan=pro_plan,
            defaults={
                "status": "ACTIVE",
                "start_date": start_date,
                "end_date": end_date,
            },
        )
        status = "CREATED" if created else "UPDATED"
        self.stdout.write(
            self.style.SUCCESS(
                f"  [{status}] PRO subscription for {subscriber_user.email} (ends: {end_date.date()})"
            )
        )

        # For free_user, we create an expired subscription to FREE plan
        # or leave them without an active subscription
        expired_start = start_date - timedelta(days=60)
        expired_end = start_date - timedelta(days=30)

        free_sub, created = SubscriptionModel.objects.update_or_create(
            user=free_user,
            plan=free_plan,
            defaults={
                "status": "CANCELED",
                "start_date": expired_start,
                "end_date": expired_end,
            },
        )
        status = "CREATED" if created else "UPDATED"
        self.stdout.write(
            self.style.SUCCESS(
                f"  [{status}] CANCELED FREE subscription for {free_user.email} (expired: {expired_end.date()})"
            )
        )

        self.stdout.write(self.style.SUCCESS("\nSuccessfully seeded subscriptions!"))
