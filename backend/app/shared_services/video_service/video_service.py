# backend/app/shared_services/video_service/video_service.py
"""
Video composition service: stitches audio, cropped background, image overlays, and animated text.
"""
import os
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from moviepy.config import change_settings

from .video_configs import IMAGEMAGICK_BINARY
from .video_utils import crop_to_vertical
from .image_overlay import build_image_overlays
from .text_overlay import build_animated_text_overlay

change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY})
logger = logging.getLogger(__name__)


def generate_video(
    script: Any,
    tts_files: List[str],
    bg_video: str,
    output_path: str,
    char_images: Optional[Dict[str, str]] = None,
    infographic_images: Optional[List[Tuple[int, str]]] = None,
) -> str:
    """
    Composes a vertical 9:16 short-form video from script dialogues, audio tracks, and visual overlays.
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    infographic_map = dict(infographic_images or [])
    char_images = char_images or {}

    bg_clip = VideoFileClip(str(bg_video))
    bg_duration = bg_clip.duration

    segments = []
    current_time = 0.0

    try:
        dialogues = getattr(script, 'dialogues', [])
        for i, (dlg, audio_path) in enumerate(zip(dialogues, tts_files)):
            if not os.path.exists(audio_path):
                logger.warning(f"Audio file not found: {audio_path}, skipping dialogue {i}")
                continue

            audio_clip = AudioFileClip(str(audio_path))
            duration = audio_clip.duration

            if duration <= 0.1:
                audio_clip.close()
                continue

            # Slices background segment (looping if duration exceeds background video)
            start_bg = current_time % bg_duration
            end_bg = start_bg + duration

            if end_bg <= bg_duration:
                bg_segment = bg_clip.subclip(start_bg, end_bg)
            else:
                sub1 = bg_clip.subclip(start_bg, bg_duration)
                sub2 = bg_clip.subclip(0, end_bg % bg_duration)
                bg_segment = concatenate_videoclips([sub1, sub2])

            current_time += duration

            # Crop background to vertical 9:16
            bg_segment = crop_to_vertical(bg_segment)
            bg_segment = bg_segment.set_audio(audio_clip)

            # Build overlays
            img_overlays = build_image_overlays(
                dlg=dlg,
                duration=duration,
                bg_segment=bg_segment,
                index=i,
                char_images=char_images,
                infographic_map=infographic_map,
            )

            try:
                txt_overlays = build_animated_text_overlay(
                    dlg=dlg,
                    duration=duration,
                    bg_segment=bg_segment,
                    used_areas=[],
                )
            except Exception as e:
                logger.warning(f"Failed to build animated text overlay for dialogue {i}: {e}")
                txt_overlays = []

            segment_clip = CompositeVideoClip([bg_segment] + (img_overlays or []) + (txt_overlays or []))
            segment_clip = segment_clip.set_duration(duration)
            segments.append(segment_clip)

        if not segments:
            raise RuntimeError("No valid video segments could be generated")

        final_clip = concatenate_videoclips(segments, method="compose")
        final_clip.write_videofile(
            str(output_file),
            codec="libx264",
            audio_codec="aac",
            fps=24,
            threads=4,
            preset="ultrafast",
            logger=None,
        )

        return str(output_file)

    finally:
        for seg in segments:
            try:
                seg.close()
            except Exception:
                pass
        try:
            bg_clip.close()
        except Exception:
            pass
