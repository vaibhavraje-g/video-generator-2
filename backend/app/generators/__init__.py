# backend/app/generators/__init__.py
"""Video generators package - plugin architecture for video types"""

from .base import BaseVideoGenerator, VideoConfig, GenerationResult, GeneratorInfo
from .registry import GeneratorRegistry

# Import all generators to trigger their @GeneratorRegistry.register decorators
# These imports must happen AFTER the registry is imported
from .family_guy import FamilyGuyGenerator
from .subliminal import SubliminalGenerator
from .frequency import FrequencyGenerator

__all__ = [
    "BaseVideoGenerator",
    "VideoConfig", 
    "GenerationResult",
    "GeneratorInfo",
    "GeneratorRegistry",
    "FamilyGuyGenerator",
    "SubliminalGenerator", 
    "FrequencyGenerator",
]
