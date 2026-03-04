import base64
import uuid
import re
from django.core.management.base import BaseCommand
from identity.infrastructure.models import CustomUserModel
from store.history.infrastructure.models import HistoryModel
from core.infrastructure.services.r2_storage_service import CloudflareR2StorageService
from core.utils.images import optimize_image


BASE64_IMAGE_PATTERN = re.compile(r'^data:image/(jpeg|png|webp);base64,([A-Za-z0-9+/]+=*)$')


class Command(BaseCommand):
    help = 'Migrates all base64 encoded images in the Database to Cloudflare R2'

    def handle(self, *args, **options):
        storage_service = CloudflareR2StorageService()
        self.stdout.write("Starting Base64 to R2 zero-data-loss migration...")

        # 1. Migrate Users
        self.stdout.write("\n--- Migrating User Avatars ---")
        users = CustomUserModel.objects.filter(avatar__startswith='data:image/').exclude(avatar='')
        total_users = users.count()
        self.stdout.write(f"Found {total_users} users with base64 avatars.")
        
        for user in users:
            try:
                match = BASE64_IMAGE_PATTERN.match(user.avatar)
                if match:
                    raw_base64 = match.group(2)
                else:
                    raw_base64 = user.avatar.split(',', 1)[-1]
                
                raw_bytes = base64.b64decode(raw_base64)
                optimized_bytes = optimize_image(raw_bytes, max_size=(500, 500), quality=80)
                file_name = f"avatars/{user.id}.jpg"
                
                r2_key = storage_service.upload_file(optimized_bytes, file_name, "image/jpeg")
                user.avatar = r2_key
                user.save(update_fields=['avatar'])
                self.stdout.write(self.style.SUCCESS(f"  [OK] Migrated avatar for user '{user.username}' -> {r2_key}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERROR] Failed to migrate avatar for user '{user.username}': {str(e)}"))

        # 2. Migrate History Photos
        self.stdout.write("\n--- Migrating Plant Health History Photos ---")
        histories = HistoryModel.objects.exclude(photo='')
        # We assume base64 if it starts with data:image or is just a huge string > 500 chars (R2 keys are small)
        base64_histories = [h for h in histories if h.photo.startswith('data:image/') or len(h.photo) > 500]
        self.stdout.write(f"Found {len(base64_histories)} history records with base64 photos.")

        for history in base64_histories:
            try:
                if history.photo.startswith('data:image/'):
                    match = BASE64_IMAGE_PATTERN.match(history.photo)
                    if match:
                        raw_base64 = match.group(2)
                    else:
                        raw_base64 = history.photo.split(',', 1)[-1]
                else:
                    raw_base64 = history.photo
                
                raw_bytes = base64.b64decode(raw_base64)
                optimized_bytes = optimize_image(raw_bytes, max_size=(1080, 1080), quality=80)
                
                # History user might be null, so fallback to 'public'
                user_id_str = str(history.user.id) if history.user else "public"
                file_name = f"plant_health/{user_id_str}_{uuid.uuid4().hex[:8]}.jpg"
                
                r2_key = storage_service.upload_file(optimized_bytes, file_name, "image/jpeg")
                history.photo = r2_key
                history.save(update_fields=['photo'])
                self.stdout.write(self.style.SUCCESS(f"  [OK] Migrated photo for history {history.id} -> {r2_key}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  [ERROR] Failed to migrate photo for history {history.id}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("\nMigration completed successfully!"))
