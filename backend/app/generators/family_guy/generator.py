# backend/app/generators/family_guy/generator.py
"""Family Guy style explainer video generator"""

import asyncio
import logging
import uuid
from pathlib import Path
from typing import Optional, Callable
from collections import defaultdict

# Setup logger for this module
logger = logging.getLogger("app.generators.family_guy")

from ..base import (
    BaseVideoGenerator,
    VideoConfig,
    GenerationResult,
    VideoDuration
)
from ..registry import GeneratorRegistry
from .prompts import VideoScript, SCRIPT_PROMPT_TEMPLATE

from app.shared_services.script_service import script_service
from app.shared_services.tts_service import TTSService
from app.shared_services.assets_service import AssetsService
from app.shared_services.video_service import generate_video
from app.core.config import settings


@GeneratorRegistry.register
class FamilyGuyGenerator(BaseVideoGenerator):
    """
    Family Guy style explainer video generator.
    
    Creates short-form educational content with:
    - Peter, Stewie, and Brian character dialogues
    - TTS voice synthesis per character
    - Character image overlays
    - Gaming/abstract background footage
    - Infographic overlays
    """
    
    @property
    def generator_id(self) -> str:
        return "family_guy"
    
    @property
    def display_name(self) -> str:
        return "Explainer (Family Guy)"
    
    @property
    def description(self) -> str:
        return "Short comedy explainer videos with Family Guy style characters discussing topics"
    
    @property
    def supported_durations(self) -> list[VideoDuration]:
        return [VideoDuration.SHORT]  # Only short form for now
    
    @property
    def config_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "style": {
                    "type": "string",
                    "enum": ["family_guy"],
                    "default": "family_guy",
                    "description": "Video style"
                },
                "background": {
                    "type": "string",
                    "enum": ["gaming", "abstract", "custom"],
                    "default": "gaming",
                    "description": "Background video type"
                },
                "background_url": {
                    "type": "string",
                    "description": "Custom background video URL (if background=custom)"
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
        """Generate a Family Guy style explainer video"""
        
        # Setup project directory
        project_dir = Path(settings.PROJECTS_DIR) / f"family_guy_{uuid.uuid4().hex[:8]}"
        project_dir.mkdir(parents=True, exist_ok=True)
        
        async def report_progress(step: str, progress: float):
            if progress_callback:
                # Ensure callback is awaited if it's async
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback(step, progress)
                else:
                    progress_callback(step, progress)
            print(f"📹 [{int(progress*100)}%] {step}")
        
        await report_progress("Generating script", 0.05)
        
        # 1. Generate script
        script = await script_service.generate_script(
            topic=topic,
            prompt_template=SCRIPT_PROMPT_TEMPLATE,
            response_model=VideoScript
        )
        print(f"✅ Generated script with {len(script.dialogues)} lines")
        
        await report_progress("Loading assets", 0.10)
        
        # 2. Initialize services
        assets_service = AssetsService(project_dir=project_dir)
        tts_service = TTSService()
        
        # 3. Load character images
        unique_characters = {d.character.lower().strip() for d in script.dialogues}
        character_images = {}
        for char in unique_characters:
            try:
                path = assets_service.get_character_image(char)
                character_images[char] = path
            except Exception as e:
                print(f"⚠️ Missing image for {char}: {e}")
        
        # 4. Get background video
        background_type = generator_config.get("background", "gaming")
        if background_type == "custom" and generator_config.get("background_url"):
            # TODO: Download custom background
            background_path = assets_service.get_stock_gameplay_footage()
        else:
            background_path = assets_service.get_stock_gameplay_footage()
        
        await report_progress("Generating audio", 0.15)
        
        # 5. Generate TTS - group by character for efficiency
        dialogues_by_char = defaultdict(list)
        for i, d in enumerate(script.dialogues):
            dialogues_by_char[d.character.lower().strip()].append((i, d))
        
        audio_paths = {}
        total_chars = len(dialogues_by_char)
        for idx, (character, items) in enumerate(dialogues_by_char.items()):
            progress = 0.15 + (0.20 * (idx / total_chars))  # 15% to 35%
            await report_progress(f"Generating voice for {character}", progress)
            
            texts = [d.text for _, d in items]
            paths = await tts_service.generate_character_batch(
                character=character,
                texts=texts,
                output_dir=str(project_dir)
            )
            
            for (orig_idx, _), path in zip(items, paths):
                audio_paths[orig_idx] = path
        
        # Reorder audio paths
        ordered_audio = [audio_paths[i] for i in range(len(script.dialogues))]
        
        await report_progress("Fetching infographics", 0.35)
        
        # 6. Fetch infographics
        infographic_paths = []
        for i, d in enumerate(script.dialogues):
            if d.infographic:
                try:
                    path = project_dir / "infographics" / f"info_{i}.jpg"
                    assets_service.get_assets_infographics(
                        query=d.infographic,
                        output_path=path
                    )
                    infographic_paths.append((i, str(path)))
                except Exception as e:
                    print(f"⚠️ Failed to fetch infographic: {e}")
        
        await report_progress("Composing video", 0.45)
        
        # 7. Compose video using the new video_service
        # This handles text overlays, character animations, and infographic positioning
        logger.info(f"Starting video composition with {len(ordered_audio)} audio clips")
        
        await report_progress("Rendering video (this may take a while)", 0.50)
        
        # 8. Generate video - Run in thread to avoid blocking event loop
        # generate_video() uses moviepy which is CPU-intensive and blocking
        output_file = await asyncio.to_thread(
            generate_video,
            script=script,
            tts_files=ordered_audio,
            bg_video=background_path,
            output_path=output_path,
            char_images=character_images,
            infographic_images=infographic_paths,
        )
        
        if not output_file:
            raise RuntimeError("Video generation failed - no output file produced")
        
        await report_progress("Complete", 1.0)
        
        # Get file size and duration
        file_size = Path(output_file).stat().st_size if Path(output_file).exists() else None
        
        # Calculate total duration from audio
        from moviepy.editor import AudioFileClip
        total_duration = 0
        for path in ordered_audio:
            try:
                clip = AudioFileClip(path)
                total_duration += clip.duration
                clip.close()
            except Exception:
                pass
        
        # Cleanup: Remove temporary project directory after successful generation
        import shutil
        try:
            # Only cleanup if video was successfully generated
            if Path(output_file).exists():
                # Remove project directory (temporary files)
                if project_dir.exists():
                    shutil.rmtree(project_dir)
                    logger.info(f"🧹 Cleaned up project directory: {project_dir}")
        except Exception as e:
            logger.warning(f"Failed to cleanup project directory {project_dir}: {e}")
            # Don't fail the generation if cleanup fails
        
        return GenerationResult(
            output_path=output_file,
            duration_seconds=total_duration,
            file_size_bytes=file_size,
            metadata={
                "topic": topic,
                "dialogue_count": len(script.dialogues),
                "characters": list(unique_characters),
                "project_dir": str(project_dir)  # Keep for reference, but dir is cleaned up
            }
        )

