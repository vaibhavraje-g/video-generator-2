# backend/app/shared_services/video_service/video_configs.py
"""
Centralized video configuration file for styling, layout, and speed control.
"""

import os

# --- Text (Subtitles) Configuration ---
TEXT_STYLE = {
    "width_ratio": 0.85,
    "max_chars_per_line": 32,      # Shorter lines for punchier look
    "max_lines": 2,
    "font": "Arial-Bold",           # Modern, clean font
    "fontsize": 52,                 # Slightly smaller for cleaner look
    "font_name": "Arial-Bold",
    "color": "white",
    "gradient_colors": ["#FFD700", "#FFA500"],
    "align": "center",
    "stroke_color": "black",
    "stroke_width": 4,              # Thicker stroke for punch
    "shadow_color": "rgba(0,0,0,0.8)",
    "shadow_offset": (4, 4),
    "pad_x": 20,
    "pad_y": 12,
    "bg_color_rgba": (255, 255, 255, 20),
    "bg_radius": 12,
    "reserve_extra": 50,
    "word_spacing": 12,
    "words_per_chunk": 3,
    "min_chunk_duration": 0.4,      # Faster pacing
    "highlight_fraction": 0.8,
    "highlight_delay_frac": 0.1,
    "highlight_color": (255, 200, 50),  # Softer gold highlight
}

TEXT_ANIMATION = {
    "fade_in": 0.15,
    "fade_out": 0.15,
    "slide_in": True,
    "slide_direction": "bottom",
    "bounce_effect": True,
    "scale_in": 1.1,
}

# --- Animation Configuration ---
ANIMATION_CONFIG = {
    "slide_duration": 0.2,      # Faster slides for punchier feel
    "fade_duration": 0.15,      # Quicker fades
    "ease_type": "cubic",
    "overshoot": 1.08,          # Slightly more bounce
    "stagger_delay": 0.03,      # Tighter stagger
}

# --- Infographic Overlay Config ---
INFOGRAPHIC_CONFIG = {
    # The infographic will be constrained to these widths/heights.
    # Large images will be downscaled to fit in this box,
    # small images will be gently upscaled (until the upscale_limit).
    "max_height": 300,
    "max_width": 500,
    "top_margin": 80,
    "animation": "slide_right",
    # how much to upscale small images (max)
    "upscale_limit": 1.25,
    # if image is smaller than this fraction of max size, apply gentle upscaling
    "upscale_threshold_frac": 0.8,
}

# --- Character Image Overlay Config ---
CHARACTER_CONFIG = {
    "max_height": 325,
    "max_width": 450,
    "bottom_margin": 30,
    "side_margin": 50,
    "animation": "slide_left",
}

# --- General Video Layout ---
VIDEO_LAYOUT = {
    "target_aspect_ratio": 9 / 16,
    "output_height": 1080,
    "output_width": 608,
    "fps": 24,
    # sections define vertical thirds roughly: top/middle/bottom fractions
    # top_section is where infographics should be visually centered.
    "top_section": 0.33,
    "middle_section": 0.34,
    "bottom_section": 0.33,
}

# --- Playback speed ---
VIDEO_SPEED = 1.05  # 5% faster for punchier pacing

# --- ImageMagick path (auto-detect or use env) ---
def get_imagemagick_path():
    """Get ImageMagick binary path from env or common locations."""
    # Check environment variable first
    env_path = os.environ.get("IMAGEMAGICK_BINARY")
    if env_path and os.path.exists(env_path):
        return env_path
    
    # Common Windows paths
    common_paths = [
        r"C:/Program Files/ImageMagick-7.1.2-Q16-HDRI/magick.exe",
        r"C:/Program Files/ImageMagick-7.1.1-Q16-HDRI/magick.exe",
        r"C:/Program Files/ImageMagick-7.1.0-Q16-HDRI/magick.exe",
        r"C:/Program Files (x86)/ImageMagick-7.1.2-Q16-HDRI/magick.exe",
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            return path
    
    # Fallback to just "magick" and hope it's in PATH
    return "magick"

IMAGEMAGICK_BINARY = get_imagemagick_path()
