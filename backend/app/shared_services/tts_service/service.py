"""Main TTS Service - Unified interface for all TTS providers"""

from pathlib import Path
from typing import Literal, Optional, List
import asyncio

from .config import TTSConfig
from .gtts_provider import GTTSProvider
from .tiktok_provider import TikTokProvider
from .chatterbox_provider import ChatterboxProvider  # now HTTP-based
from .subtitle_service import SubtitleService
from .text_preprocessor import TTSPreprocessor


class TTSService:
    """
    Unified TTS Service supporting multiple providers:
    - ChatterboxTTS (via remote HTTP API) for character voice cloning
    - gTTS for basic TTS with voice options
    - TikTok API for free high-quality TTS
    - Local subtitle generation
    """

    def __init__(self, config_path: str = None, project_dir: Optional[Path] = None):
        self.config = TTSConfig(config_path)
        self.project_dir = project_dir

        self.voice_samples_dir = self.config.get_voice_samples_dir()
        self.outputs_dir = self.config.get_outputs_dir()

        self.tiktok_provider = TikTokProvider(self.config.get_tiktok_config())
        self.gtts_provider = GTTSProvider(outputs_dir=self.outputs_dir)

        # 🔁 Updated: Initialize HTTP-based Chatterbox provider
        chatterbox_config = self.config.get_chatterbox_config()
        base_url = chatterbox_config.get("base_url", "http://localhost:8004")

        self.chatterbox_provider = ChatterboxProvider(
            character_voices=chatterbox_config.get("character_voices", {}),
            character_mappings=chatterbox_config.get("character_mappings", {}),
            voice_samples_dir=self.voice_samples_dir,  # still used if auto-uploading
            outputs_dir=self.outputs_dir,
            base_url=base_url,  # ✅ new parameter
        )

        self.subtitle_service = SubtitleService(self.config.get_subtitle_config())
        self.preprocessor = TTSPreprocessor()

    # --- Unified Generation API ---
    def generate(
        self,
        text: str,
        output_path: str,
        provider: Literal["chatterbox", "gtts", "tiktok"] = "gtts",
        **kwargs,
    ) -> str:
        clean_text = self.preprocessor.clean(text)

        if provider == "chatterbox":
            character = kwargs.pop("character", None)
            if not character:
                raise ValueError("Character name required for chatterbox provider")
            return self.generate_character_voice(clean_text, character, output_path, **kwargs)
        elif provider == "tiktok":
            return self.generate_tiktok_tts(clean_text, output_path, **kwargs)
        else:
            return self.generate_gtts(clean_text, output_path, **kwargs)

    # --- Individual Provider Methods ---
    def generate_character_voice(self, text: str, character: str, output_path: str, **kwargs) -> str:
        try:
            return self.chatterbox_provider.generate(text, character, output_path, **kwargs)
        except Exception as e:
            print(f"WARNING: Character TTS failed: {e}")
            print("Falling back to gTTS...")
            return self.generate_gtts(text, output_path)

    def generate_gtts(self, text: str, output_path: str, voice: Literal["male", "female"] = "male", lang: str = "en", slow: bool = False) -> str:
        return self.gtts_provider.generate(text, output_path, voice=voice, lang=lang, slow=slow)

    def generate_tiktok_tts(self, text: str, output_path: str, voice_id: str = None, project_dir: Optional[Path] = None, **kwargs) -> str:
        try:
            return self.tiktok_provider.generate(
                text,
                output_path,
                voice_id=voice_id,
                project_dir=project_dir or self.project_dir,
                **kwargs,
            )
        except Exception as e:
            print(f"WARNING: TikTok TTS failed: {e}")
            print("Falling back to gTTS...")
            return self.generate_gtts(text, output_path)

    # --- Subtitles ---
    def generate_subtitles(self, sentences: list, audio_clips: list) -> str:
        return self.subtitle_service.generate_subtitles(sentences, audio_clips)

    def add_subtitles_to_video(
        self,
        video_path: str,
        subtitles_path: str,
        output_path: str,
        position: str = "center,bottom",
        font_path: str = None,
        font_size: int = 100,
        color: str = "white",
        stroke_color: str = "black",
        stroke_width: int = 5,
        threads: int = 2,
    ) -> str:
        return self.subtitle_service.add_subtitles_to_video(
            video_path, subtitles_path, output_path,
            position, font_path, font_size, color, stroke_color, stroke_width, threads
        )

    async def generate_character_batch(self, character: str, texts: list[str], output_dir: str):
        """
        Efficiently generate TTS for multiple lines of one character.
        Uses Chatterbox voice cloning only once (via HTTP).
        Falls back to gTTS if Chatterbox is unavailable.
        """
        from pathlib import Path

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        audio_paths = []
        
        # Check if voice file exists for Chatterbox
        wav_file = Path(self.voice_samples_dir) / f"{character}_voice.wav"
        mp3_file = Path(self.voice_samples_dir) / f"{character}_voice.mp3"
        
        use_chatterbox = False
        local_voice_file = None
        
        if wav_file.exists():
            local_voice_file = wav_file
            use_chatterbox = True
        elif mp3_file.exists():
            local_voice_file = mp3_file
            use_chatterbox = True
        else:
            print(f"⚠️ No voice sample for '{character}', using gTTS fallback")

        for i, text in enumerate(texts):
            output_path = output_dir / f"{character}_{i}.wav"
            clean_text = self.preprocessor.clean(text) if text else ""
            
            # Skip empty texts - generate placeholder audio
            if not clean_text or not clean_text.strip():
                print(f"⚠️ Empty text for {character}_{i}, using placeholder")
                clean_text = "Next."  # Minimal speakable text for TTS
            
            if use_chatterbox:
                try:
                    audio_path = await asyncio.to_thread(
                        self.chatterbox_provider.generate,
                        text=clean_text,
                        reference_audio_path=str(local_voice_file),
                        output_path=str(output_path),
                    )
                    audio_paths.append(str(output_path))
                except Exception as e:
                    print(f"⚠️ Chatterbox TTS failed for '{character}': {e}")
                    print("   Falling back to gTTS...")
                    # Fall back to gTTS
                    mp3_path = str(output_path).replace('.wav', '.mp3')
                    self.gtts_provider.generate(clean_text, mp3_path)
                    audio_paths.append(mp3_path)
            else:
                # Use gTTS directly
                mp3_path = str(output_path).replace('.wav', '.mp3')
                self.gtts_provider.generate(clean_text, mp3_path)
                audio_paths.append(mp3_path)

        return audio_paths
