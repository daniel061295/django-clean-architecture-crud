"""
Identity Utils — Utility functions for the Identity bounded context.
"""
import base64
from pathlib import Path
from django.conf import settings

# Cache for default avatar to avoid reading file multiple times
_DEFAULT_AVATAR_CACHE: str | None = None


def get_default_user_avatar() -> str:
    """
    Returns the fixed R2 object key for the default avatar.
    """
    return "avatars/default.jpg"

def get_default_user_avatar_base64() -> str:
    """
    Returns the default user avatar as a base64 encoded data URI.
    Used for initial uploads.
    """
    global _DEFAULT_AVATAR_CACHE
    
    if _DEFAULT_AVATAR_CACHE is not None:
        return _DEFAULT_AVATAR_CACHE
    
    avatar_path = settings.BASE_DIR / "avatar.jpg"
    if not avatar_path.exists():
        return ""
    
    with open(avatar_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    _DEFAULT_AVATAR_CACHE = f"data:image/jpeg;base64,{image_data}"
    return _DEFAULT_AVATAR_CACHE
