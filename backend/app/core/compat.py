# backend/app/core/compat.py
"""
Compatibility patches for third-party library issues.
Import this at application startup to apply patches.
"""

def patch_pillow_antialias():
    """
    Fix for MoviePy + Pillow 10+ compatibility issue.
    
    Pillow 10.0.0 removed Image.ANTIALIAS in favor of Image.Resampling.LANCZOS.
    MoviePy 1.0.3 still uses the old ANTIALIAS constant, causing:
        AttributeError: module 'PIL.Image' has no attribute 'ANTIALIAS'
    
    This patch adds ANTIALIAS as an alias for LANCZOS.
    """
    from PIL import Image
    
    if not hasattr(Image, 'ANTIALIAS'):
        # Pillow 10+ removed ANTIALIAS, add it back as alias
        Image.ANTIALIAS = Image.Resampling.LANCZOS
        print("✅ Applied Pillow ANTIALIAS compatibility patch")


def apply_all_patches():
    """Apply all compatibility patches"""
    patch_pillow_antialias()


# Auto-apply patches when module is imported
apply_all_patches()
