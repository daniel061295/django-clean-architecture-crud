import json
from django.core.management.base import BaseCommand
from store.tips.application.use_cases import CreateTipUseCase
from store.tips.application.dtos import CreateTipInputDTO
from injector import Injector
from store.di import StoreModule

class Command(BaseCommand):
    help = 'Seeds the database with gardening tips'

    def handle(self, *args, **kwargs):
        tips_data = [
            { "title": "Lighting Tip", "description": "Most indoor plants prefer bright indirect light. Avoid direct sunlight to prevent leaf burn.", "icon": "sun" },
            { "title": "Watering Tip", "description": "Before watering, stick your finger 2-3 cm into the soil. If it feels dry, it's time to water.", "icon": "droplet" },
            { "title": "Cleaning Tip", "description": "Wipe dust off leaves with a damp cloth. This helps the plant breathe and photosynthesize better.", "icon": "leaf" },
            { "title": "Humidity Tip", "description": "If leaf tips are turning brown, your plant may need more humidity. Try misting or using a humidifier.", "icon": "mist" },
            { "title": "Drainage Tip", "description": "Always ensure your pot has drainage holes to prevent root rot caused by standing water.", "icon": "bucket" },
            { "title": "Growth Tip", "description": "Rotate your plant 90 degrees every week so it grows evenly and doesn't lean toward the light.", "icon": "rotate-clockwise" },
            { "title": "Fertilizing Tip", "description": "Only fertilize your plants during spring and summer when they are in their active growth phase.", "icon": "flask-2" },
            { "title": "Repotting Tip", "description": "If roots are growing out of the drainage holes, it is time to move your plant to a slightly larger pot.", "icon": "arrows-maximize" },
            { "title": "Temperature Tip", "description": "Keep plants away from cold drafts or direct heat vents; sudden temperature changes can cause stress.", "icon": "thermometer-half" },
            { "title": "Pest Tip", "description": "Check the underside of leaves regularly. Detecting small invaders early is key to saving your plant.", "icon": "bug" },
            { "title": "Pruning Tip", "description": "Trim yellow or dead leaves. This helps the plant focus its energy on healthy new growth.", "icon": "scissors" },
            { "title": "Water Quality Tip", "description": "If using tap water, let it sit for 24 hours before watering to allow chlorine to evaporate.", "icon": "ripple" },
            { "title": "Potting Tip", "description": "Terra cotta pots help soil dry out faster, which is ideal for succulents and cacti.", "icon": "plant" },
            { "title": "Winter Tip", "description": "In winter, reduce watering frequency. Plants go dormant and need much less moisture.", "icon": "snowflake" },
            { "title": "Grouping Tip", "description": "Group several plants together. This creates a beneficial microclimate of shared humidity.", "icon": "friends" }
        ]

        injector = Injector([StoreModule()])
        create_use_case = injector.get(CreateTipUseCase)

        created_count = 0
        for tip in tips_data:
            input_dto = CreateTipInputDTO(
                title=tip["title"],
                description=tip["description"],
                icon=tip["icon"]
            )
            create_use_case.execute(input_dto)
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {created_count} tips!'))
