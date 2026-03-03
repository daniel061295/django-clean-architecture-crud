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
    Returns the default user avatar as a base64 encoded data URI.
    
    The avatar is loaded from the avatar.jpg file in the project root.
    Result is cached to avoid repeated file I/O.
    
    Returns:
        str: Data URI with base64 encoded JPEG image.
    """
    global _DEFAULT_AVATAR_CACHE
    
    if _DEFAULT_AVATAR_CACHE is not None:
        return _DEFAULT_AVATAR_CACHE
    
    # Path to avatar file (project root using Django BASE_DIR)
    avatar_path = settings.BASE_DIR / "avatar.jpg"
    
    if not avatar_path.exists():
        # Return empty string if file not found
        return ""
    
    # Read and encode the image
    with open(avatar_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    # Cache and return as data URI
    _DEFAULT_AVATAR_CACHE = f"data:image/jpeg;base64,{image_data}"
    return _DEFAULT_AVATAR_CACHE
