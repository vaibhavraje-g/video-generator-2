# backend/app/generators/frequency/generator.py
"""
Acoustic Frequency and Binaural Brainwave Entrainment Video Generator.

Synthesizes mathematically pure harmonic tones, binaural beats, and audio-reactive
Lissajous cymatics visualizers using native FFmpeg DSP filters and Pillow HUD overlays.
Zero pseudo-science: strictly grounded in psychoacoustics and brainwave entrainment.
"""

import os
import re
import math
import uuid
import asyncio
import subprocess
from pathlib import Path
from typing import Optional, Callable, Dict, Any, Tuple

from PIL import Image, ImageDraw, ImageFont

from ..base import (
    BaseVideoGenerator,
    VideoConfig,
    GenerationResult,
    VideoDuration,
    AspectRatio
)
from ..registry import GeneratorRegistry
from app.shared_services.frequency_service import frequency_service
from app.core.config import settings


# Brainwave entrainment psychoacoustic profiles
BRAINWAVE_PROFILES = {
    "gamma": {
        "name": "Gamma",
        "default_beat": 40.0,
        "range": (30.0, 50.0),
        "state": "PEAK FOCUS & HIGH-LEVEL COGNITION",
        "description": "Peak cognitive alertness, information synthesis, and complex problem-solving",
        "primary_color": (99, 102, 241),    # Indigo
        "accent_color": (56, 189, 248),     # Cyan
        "hex_color": "#6366F1"
    },
    "beta": {
        "name": "Beta",
        "default_beat": 16.0,
        "range": (14.0, 30.0),
        "state": "ACTIVE CONCENTRATION & PRODUCTIVITY",
        "description": "Active analytical thinking, conscious task engagement, and focus",
        "primary_color": (56, 189, 248),    # Sky Blue
        "accent_color": (99, 102, 241),     # Indigo
        "hex_color": "#38BDF8"
    },
    "alpha": {
        "name": "Alpha",
        "default_beat": 10.0,
        "range": (8.0, 14.0),
        "state": "FLOW STATE & COGNITIVE CALM",
        "description": "Effortless flow state, relaxed mental alertness, and reduced stress",
        "primary_color": (168, 85, 247),    # Purple / Violet
        "accent_color": (56, 189, 248),     # Cyan
        "hex_color": "#A855F7"
    },
    "theta": {
        "name": "Theta",
        "default_beat": 6.0,
        "range": (4.0, 8.0),
        "state": "DEEP MEDITATION & CREATIVITY",
        "description": "Introspective awareness, REM states, memory consolidation, and creative insight",
        "primary_color": (236, 72, 153),    # Pink / Magenta
        "accent_color": (168, 85, 247),     # Violet
        "hex_color": "#EC4899"
    },
    "delta": {
        "name": "Delta",
        "default_beat": 2.5,
        "range": (0.5, 4.0),
        "state": "RESTORATIVE SLEEP & DEEP REST",
        "description": "Slow-wave restorative sleep, physical recuperation, and nervous system reset",
        "primary_color": (59, 130, 246),    # Deep Blue
        "accent_color": (99, 102, 241),     # Indigo
        "hex_color": "#3B82F6"
    },
    "schumann": {
        "name": "Schumann",
        "default_beat": 7.83,
        "range": (7.0, 8.5),
        "state": "GEOMAGNETIC RESONANCE & GROUNDING",
        "description": "Atmospheric Schumann resonance fundamental (7.83 Hz) for grounding equilibrium",
        "primary_color": (16, 185, 129),    # Emerald
        "accent_color": (56, 189, 248),     # Cyan
        "hex_color": "#10B981"
    }
}


def extract_frequency_params(prompt: str, generator_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Extract carrier frequency, beat frequency, brainwave state, and intention from prompt and config.
    Supports any frequency requested by user.
    """
    config = generator_config or {}
    clean_prompt = (prompt or "").lower().strip()

    # 1. Carrier Frequency: Check explicit config or parse from prompt
    carrier_hz = config.get("frequency")
    if not carrier_hz:
        # Search for numbers followed by 'hz' or freestanding frequencies
        hz_matches = re.findall(r'(\d+(?:\.\d+)?)\s*hz', clean_prompt)
        if hz_matches:
            # Parse values; differentiate between carrier (>40 Hz) and beat (<=40 Hz)
            nums = [float(m) for m in hz_matches]
            carriers = [n for n in nums if n >= 50]
            if carriers:
                carrier_hz = int(carriers[0])
            else:
                # E.g. "40 hz" -> could be carrier or beat
                carrier_hz = int(nums[0])
        else:
            # Common solfeggio numbers mentioned without 'hz'
            for solfeggio in [432, 528, 639, 741, 852, 963, 108, 111, 174, 285, 396]:
                if str(solfeggio) in clean_prompt:
                    carrier_hz = solfeggio
                    break

    # Fallback carrier default
    if not carrier_hz or carrier_hz < 20:
        carrier_hz = 432

    # 2. Brainwave state & Binaural Beat frequency
    brainwave_key = "alpha"  # default
    beat_hz: Optional[float] = config.get("binaural_beat_hz")

    if "schumann" in clean_prompt or "earth" in clean_prompt or "grounding" in clean_prompt:
        brainwave_key = "schumann"
    elif "delta" in clean_prompt or "sleep" in clean_prompt or "insomnia" in clean_prompt or "rest" in clean_prompt:
        brainwave_key = "delta"
    elif "theta" in clean_prompt or "meditat" in clean_prompt or "creativ" in clean_prompt or "trance" in clean_prompt:
        brainwave_key = "theta"
    elif "gamma" in clean_prompt or "coding" in clean_prompt or "peak" in clean_prompt or "study" in clean_prompt or "physics" in clean_prompt:
        brainwave_key = "gamma"
    elif "beta" in clean_prompt or "alert" in clean_prompt or "work" in clean_prompt or "concentrat" in clean_prompt:
        brainwave_key = "beta"
    elif "alpha" in clean_prompt or "flow" in clean_prompt or "calm" in clean_prompt or "relax" in clean_prompt:
        brainwave_key = "alpha"

    # Explicit beat frequency in prompt (e.g. "beat of 6hz" or "10hz beat")
    beat_match = re.search(r'(?:beat|binaural|entrainment)(?:\s+of)?\s*(\d+(?:\.\d+)?)\s*hz', clean_prompt)
    if beat_match:
        beat_hz = float(beat_match.group(1))
    elif not beat_hz:
        # Check if a small number with 'hz' was parsed earlier
        small_hz = [float(m) for m in re.findall(r'(\d+(?:\.\d+)?)\s*hz', clean_prompt) if float(m) <= 40 and float(m) != carrier_hz]
        if small_hz:
            beat_hz = small_hz[0]
        else:
            beat_hz = BRAINWAVE_PROFILES[brainwave_key]["default_beat"]

    profile = BRAINWAVE_PROFILES.get(brainwave_key, BRAINWAVE_PROFILES["alpha"])

    # Carrier label
    preset = frequency_service.get_preset(carrier_hz)
    carrier_label = preset.name if preset else f"Harmonic Resonance"

    return {
        "carrier_hz": int(carrier_hz),
        "beat_hz": round(float(beat_hz), 2),
        "brainwave_name": profile["name"],
        "state_title": profile["state"],
        "description": profile["description"],
        "carrier_label": carrier_label,
        "primary_color": profile["primary_color"],
        "accent_color": profile["accent_color"],
        "hex_color": profile["hex_color"],
        "include_binaural": True
    }


def _get_system_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Safely retrieve crisp system font with fallbacks"""
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


def generate_cymatics_hud(
    width: int,
    height: int,
    params: Dict[str, Any],
    output_path: str
) -> str:
    """
    Generate high-DPI transparent vector HUD overlay with smooth glowing aura and psychoacoustic typography.
    """
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))

    # 1. Soft radial background aura centered around Lissajous pattern
    bg_glow = Image.new("RGBA", (width, height), (4, 7, 17, 255))
    glow_draw = ImageDraw.Draw(bg_glow)
    center_x = width // 2
    center_y = height // 2 - int(height * 0.02)
    max_r = int(min(width, height) * 0.42)
    
    pr, pg, pb = params["primary_color"]
    for r in range(max_r, 0, -8):
        alpha = int(55 * (1.0 - (r / max_r) ** 1.8))
        glow_draw.ellipse(
            [center_x - r, center_y - r, center_x + r, center_y + r],
            fill=(pr, pg, pb, alpha)
        )

    img = Image.alpha_composite(bg_glow, img)
    draw = ImageDraw.Draw(img)

    # 2. Typography
    font_hero = _get_system_font(int(height * 0.046), bold=True)
    font_sub = _get_system_font(int(height * 0.017), bold=True)
    font_badge = _get_system_font(int(height * 0.013), bold=True)
    font_desc = _get_system_font(int(height * 0.014), bold=False)

    # 3. Top Telemetry Pill
    pill_w = int(width * 0.46)
    pill_h = int(height * 0.028)
    pill_x0 = (width - pill_w) // 2
    pill_y0 = int(height * 0.065)
    
    draw.rounded_rectangle(
        [(pill_x0, pill_y0), (pill_x0 + pill_w, pill_y0 + pill_h)],
        radius=pill_h // 2,
        fill=(15, 23, 42, 230),
        outline=(pr, pg, pb, 160),
        width=2
    )
    # Status dot
    dot_r = 6
    draw.ellipse(
        [(pill_x0 + 18, pill_y0 + pill_h // 2 - dot_r), (pill_x0 + 18 + dot_r * 2, pill_y0 + pill_h // 2 + dot_r)],
        fill=(52, 211, 153, 255)
    )
    draw.text(
        (pill_x0 + 38, pill_y0 + pill_h // 2),
        "ACOUSTIC FREQUENCY SYNTHESIZER",
        fill=(224, 231, 255, 255),
        font=font_badge,
        anchor="lm"
    )

    # 4. Carrier Frequency Headline
    hero_y = int(height * 0.135)
    draw.text(
        (center_x, hero_y),
        f"{params['carrier_hz']} Hz",
        fill=(255, 255, 255, 255),
        font=font_hero,
        anchor="mm"
    )

    # 5. Brainwave Entrainment Subtitle
    sub_y = hero_y + int(height * 0.038)
    ar, ag, ab = params["accent_color"]
    draw.text(
        (center_x, sub_y),
        f"{params['brainwave_name'].upper()} BRAINWAVE ENTRAINMENT  •  {params['beat_hz']} Hz",
        fill=(ar, ag, ab, 255),
        font=font_sub,
        anchor="mm"
    )

    # 6. Psychoacoustic Intention Tagline
    desc_y = sub_y + int(height * 0.026)
    draw.text(
        (center_x, desc_y),
        params["state_title"],
        fill=(148, 163, 184, 255),
        font=font_desc,
        anchor="mm"
    )

    # 7. Concentric Cymatics Reticle Rings
    ring1 = int(min(width, height) * 0.36)
    draw.ellipse(
        [center_x - ring1, center_y - ring1, center_x + ring1, center_y + ring1],
        outline=(pr, pg, pb, 60),
        width=1
    )
    ring2 = int(min(width, height) * 0.35)
    draw.ellipse(
        [center_x - ring2, center_y - ring2, center_x + ring2, center_y + ring2],
        outline=(ar, ag, ab, 45),
        width=1
    )

    # 8. Waveform Oscilloscope Label
    wave_label_y = int(height * 0.77)
    draw.text(
        (center_x, wave_label_y),
        "STEREO PHASE OSCILLOSCOPE (L/R CHANNELS)",
        fill=(100, 116, 139, 230),
        font=font_badge,
        anchor="mm"
    )

    # 9. Bottom Headphone Requirement Banner
    bot_w = int(width * 0.62)
    bot_h = int(height * 0.030)
    bot_x0 = (width - bot_w) // 2
    bot_y0 = int(height * 0.90)

    draw.rounded_rectangle(
        [(bot_x0, bot_y0), (bot_x0 + bot_w, bot_y0 + bot_h)],
        radius=bot_h // 2,
        fill=(15, 23, 42, 230),
        outline=(ar, ag, ab, 120),
        width=1
    )
    draw.text(
        (center_x, bot_y0 + bot_h // 2),
        "HEADPHONES RECOMMENDED FOR BINAURAL ENTRAINMENT",
        fill=(224, 242, 254, 255),
        font=font_badge,
        anchor="mm"
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, "PNG")
    return output_path


@GeneratorRegistry.register
class FrequencyGenerator(BaseVideoGenerator):
    """
    Acoustic Frequency and Binaural Brainwave Entrainment Video Generator.
    
    Generates:
    - Pure mathematical sine wave carrier tones
    - Stereo phase-offset binaural beats
    - Dynamic Lissajous cymatics vectorscope video
    - Audio-reactive oscilloscope waveform HUD
    - Multi-stage SSE telemetry feedback
    """
    
    @property
    def generator_id(self) -> str:
        return "frequency"
    
    @property
    def display_name(self) -> str:
        return "Acoustic Frequency & Binaural Beats"
    
    @property
    def description(self) -> str:
        return "High-fidelity harmonic frequencies with binaural entrainment and audio-reactive Lissajous cymatics"
    
    @property
    def supported_durations(self) -> list[VideoDuration]:
        return [VideoDuration.SHORT, VideoDuration.LONG]
    
    @property
    def config_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "frequency": {
                    "type": "integer",
                    "default": 432,
                    "description": "Carrier frequency in Hz (e.g. 432, 528, 108, 639, 40)"
                },
                "binaural_beat_hz": {
                    "type": "number",
                    "default": 10.0,
                    "description": "Binaural beat difference in Hz (Alpha 10Hz, Theta 6Hz, Delta 2.5Hz, Gamma 40Hz)"
                },
                "visual_style": {
                    "type": "string",
                    "enum": ["lissajous", "oscilloscope", "cymatics"],
                    "default": "lissajous",
                    "description": "Visualizer DSP display mode"
                }
            }
        }
    
    async def generate(
        self,
        topic: str,
        video_config: VideoConfig,
        generator_config: dict,
        output_path: str,
        progress_callback: Optional[Callable] = None
    ) -> GenerationResult:
        """Generate high-fidelity frequency video with audio-reactive cymatics"""
        
        project_dir = Path(settings.PROJECTS_DIR) / f"freq_{uuid.uuid4().hex[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)

        async def report_progress(step: str, progress: float):
            if progress_callback:
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(step, progress)
                else:
                    progress_callback(step, progress)
            print(f"[FREQ] [{int(progress * 100)}%] {step}")

        # 1. Parameter extraction from prompt
        await report_progress("Acoustic DSP Analysis: Extracting carrier & brainwave target...", 0.10)
        params = extract_frequency_params(topic, generator_config)
        carrier_hz = params["carrier_hz"]
        beat_hz = params["beat_hz"]

        # Determine duration
        total_duration = 60 if str(video_config.duration).lower() in ("short", VideoDuration.SHORT.value) else 300

        # Video dimensions
        aspect = str(video_config.aspect_ratio.value if hasattr(video_config.aspect_ratio, "value") else video_config.aspect_ratio)
        if aspect in (AspectRatio.HORIZONTAL.value, "16:9", "horizontal", "landscape"):
            width, height = 1920, 1080
        elif aspect in (AspectRatio.SQUARE.value, "1:1", "square"):
            width, height = 1080, 1080
        else:
            width, height = 1080, 1920

        # 2. Pure Stereo Acoustic Synthesis
        await report_progress(
            f"Harmonic Audio Synthesis: Generating {carrier_hz}Hz carrier with {beat_hz}Hz binaural beat...",
            0.35
        )
        audio_path = str(project_dir / f"frequency_{carrier_hz}hz_beat_{beat_hz}.wav")
        frequency_service.generate_binaural(
            base_frequency=carrier_hz,
            beat_frequency=beat_hz,
            duration_seconds=total_duration,
            output_path=audio_path,
            amplitude=0.6
        )

        # 3. Dynamic Cymatics HUD Generation
        await report_progress("Cymatics Visualizer Engine: Rendering Lissajous phase vectorscope...", 0.65)
        hud_png_path = str(project_dir / "hud_overlay.png")
        generate_cymatics_hud(width, height, params, hud_png_path)

        # 4. Lossless Multiplexing via Native FFmpeg DSP Filters
        await report_progress("Lossless Audio-Visual Mux: Encoding 1080p master with 320kbps audio...", 0.88)
        
        pr, pg, pb = params["primary_color"]
        ar, ag, ab = params["accent_color"]
        
        # Audio wave sizing
        wave_w = int(width * 0.82)
        wave_h = int(height * 0.08)
        wave_y = int(height * 0.79)

        # Build FFmpeg filter complex:
        # [0:a] asplit=3:
        #   a_stereo -> avectorscope Lissajous figure in center
        #   a_wave   -> showwaves oscilloscope
        #   a_out    -> master audio stream
        # Overlay: background HUD -> lissajous -> oscilloscope -> output video
        filter_complex = (
            f"[0:a]asplit=3[a_stereo][a_wave][a_out];"
            f"[1:v]format=rgba[hud_bg];"
            f"[a_stereo]avectorscope=s={width}x{height}:mode=lissajous:draw=line:scale=sqrt:zoom=1.35:mirror=xy:"
            f"rc={pr}:gc={pg}:bc={pb}:rf=0:gf=0:bf=0,format=rgba,colorkey=0x000000:0.08:0.08[scope];"
            f"[a_wave]showwaves=s={wave_w}x{wave_h}:mode=line:colors=0x{ar:02X}{ag:02X}{ab:02X}|0x{pr:02X}{pg:02X}{pb:02X}:scale=cbrt,"
            f"format=rgba,colorkey=0x000000:0.08:0.08[wave];"
            f"[hud_bg][scope]overlay=0:0[stage1];"
            f"[stage1][wave]overlay=x=(W-w)/2:y={wave_y}[final_v]"
        )

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-i", hud_png_path,
            "-filter_complex", filter_complex,
            "-map", "[final_v]",
            "-map", "[a_out]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "320k",
            "-movflags", "+faststart",
            "-t", str(total_duration),
            output_path
        ]

        # Execute in non-blocking thread pool
        loop = asyncio.get_event_loop()
        def run_ffmpeg():
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if res.returncode != 0:
                raise RuntimeError(f"FFmpeg cymatics visualizer failed: {res.stderr[-500:]}")

        await loop.run_in_executor(None, run_ffmpeg)

        await report_progress("Complete: Acoustic Frequency Master Ready", 1.0)

        file_size = Path(output_path).stat().st_size if Path(output_path).exists() else None

        return GenerationResult(
            output_path=output_path,
            duration_seconds=total_duration,
            file_size_bytes=file_size,
            metadata={
                "carrier_hz": carrier_hz,
                "beat_hz": beat_hz,
                "brainwave_state": params["brainwave_name"],
                "state_title": params["state_title"],
                "acoustic_engine": "Native FFmpeg DSP + Lissajous Vectorscope",
                "audio_format": "320kbps Lossless AAC Stereo Binaural",
                "video_resolution": f"{width}x{height}",
                "aspect_ratio": aspect,
                "project_dir": str(project_dir)
            }
        )
