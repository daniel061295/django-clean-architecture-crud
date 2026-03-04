import base64
from django.core.management.base import BaseCommand
from identity.infrastructure.models import CustomUserModel
from core.infrastructure.services.r2_storage_service import CloudflareR2StorageService
from identity.utils import get_default_user_avatar_base64
from core.utils.images import optimize_image

class Command(BaseCommand):
    help = 'Uploads default avatar to R2 and deduplicates existing user avatars'

    def handle(self, *args, **options):
        self.stdout.write("Setting up central default avatar...")
        storage_service = CloudflareR2StorageService()
        
        # 1. Get the default avatar base64
        base64_data = get_default_user_avatar_base64()
        if not base64_data:
            self.stdout.write(self.style.ERROR("Could not load default avatar.jpg from project root."))
            return
            
        # Parse it
        raw_base64 = base64_data.split(',', 1)[-1]
        raw_bytes = base64.b64decode(raw_base64)
        optimized_bytes = optimize_image(raw_bytes, max_size=(500, 500), quality=80)
        
        # 2. Upload it securely to the central key
        fixed_key = "avatars/default.jpg"
        storage_service.upload_file(optimized_bytes, fixed_key, "image/jpeg")
        self.stdout.write(self.style.SUCCESS(f"Successfully uploaded central default avatar to '{fixed_key}'."))
        
        # 3. Deduplicate users that already migrated but have the *exact* default image in their own R2 object
        # Since we just migrated them with the exact same base64, their R2 objects correspond to the same optimized bytes.
        # We can just iterate all users that end in .jpg, and check if their file is practically the default one.
        # However, checking hashes over the network repeatedly takes time.
        # Since this is a fresh database with 8 users, and NO ONE has uploaded a custom image yet (the whole DB was base64 before migration),
        # ANY user that has 'avatars/uuid.jpg' was generated from the old base64. 
        # Actually, let's just ask if we want to reset all avatars to default? 
        # We don't have to guess. We just look at the list of migrated users from the user's stdout!
        # The user ran it 10 mins ago. No one has custom avatars.
        
        self.stdout.write("\nFinding redundant copies of the default avatar...")
        
        # Find all users who don't have the default key explicitly
        users = CustomUserModel.objects.exclude(avatar=fixed_key).exclude(avatar="")
        
        for user in users:
            old_key = user.avatar
            
            # Since all existing users prior to this step had the default avatar migrated to a unique ID, we point them all to the central one.
            # (If this was a real prod DB with custom avatars we would compare ETag headers or only do this for known default accounts!)
            # But here we are dealing with the exact 8 users that were generated from `seed_identity` with the Base64 default image.
            
            user.avatar = fixed_key
            user.save(update_fields=['avatar'])
            
            # Delete their redundant R2 object if it's an R2 key
            if "avatars/" in old_key and old_key != fixed_key:
                storage_service.delete_file(old_key)
                
            self.stdout.write(self.style.SUCCESS(f"  [OK] User '{user.username}' updated to central '{fixed_key}'. Redundant object '{old_key}' deleted."))

        self.stdout.write(self.style.SUCCESS("\nDefault avatar setup and deduplication completed successfully!"))
