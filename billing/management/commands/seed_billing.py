"""
Django management command to seed billing plans.
"""
from django.core.management.base import BaseCommand

from billing.models import PlanModel


class Command(BaseCommand):
    """Command to seed the database with billing plans."""

    help = "Seed the database with FREE and PRO billing plans"

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Starting billing plans seed...")

        # Create or update FREE plan
        free_plan, created = PlanModel.objects.update_or_create(
            name="FREE",
            defaults={
                "price": 0.00,
                "scan_limit_per_day": 5,
                "ads_enabled": True,
                "features": {"tier": "free"},
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  [CREATED] FREE plan: {free_plan.id}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  [UPDATED] FREE plan: {free_plan.id}'))

        # Create or update PRO plan
        pro_plan, created = PlanModel.objects.update_or_create(
            name="PRO",
            defaults={
                "price": 9.99,
                "scan_limit_per_day": 20,
                "ads_enabled": False,
                "features": {"tier": "pro"},
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'  [CREATED] PRO plan: {pro_plan.id}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'  [UPDATED] PRO plan: {pro_plan.id}'))

        self.stdout.write(self.style.SUCCESS("\nSuccessfully seeded billing plans!"))
