# backend/app/shared_services/video_service/__init__.py
"""Video composition service with animations and overlays"""

from .video_service import generate_video
from .video_configs import (
    TEXT_STYLE,
    TEXT_ANIMATION,
    ANIMATION_CONFIG,
    INFOGRAPHIC_CONFIG,
    CHARACTER_CONFIG,
    VIDEO_LAYOUT,
    VIDEO_SPEED,
)

__all__ = [
    "generate_video",
    "TEXT_STYLE",
    "TEXT_ANIMATION", 
    "ANIMATION_CONFIG",
    "INFOGRAPHIC_CONFIG",
    "CHARACTER_CONFIG",
    "VIDEO_LAYOUT",
    "VIDEO_SPEED",
]
