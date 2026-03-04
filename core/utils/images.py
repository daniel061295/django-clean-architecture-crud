from io import BytesIO
from PIL import Image


def optimize_image(image_bytes: bytes, max_size: tuple[int, int] = (1080, 1080), quality: int = 80) -> bytes:
    """
    Optimizes an image by resizing it and compressing it to JPEG format.
    
    Args:
        image_bytes: The raw bytes of the image.
        max_size: Maximum dimensions (width, height). Aspect ratio is maintained.
        quality: JPEG compression quality (0-100).
        
    Returns:
        The optimized image bytes, or the original bytes if optimization fails.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if it has an alpha channel or is paletted
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
            
        # Resize using LANCZOS filter for best quality
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        output = BytesIO()
        img.save(output, format="JPEG", quality=quality)
        return output.getvalue()
    except Exception:
        # Fallback to original bytes if it's not a valid image format Pillow can handle
        return image_bytes
