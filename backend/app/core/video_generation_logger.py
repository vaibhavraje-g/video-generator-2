# backend/app/core/video_generation_logger.py
"""
Dedicated logger for video generation pipeline.
Logs to both console and file for debugging video generation issues.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class VideoGenerationLogger:
    """
    Specialized logger for video generation pipeline.
    Logs all steps and errors to a dedicated file for debugging.
    """
    
    _instance: Optional['VideoGenerationLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Setup the video generation logger with file and console handlers"""
        self._logger = logging.getLogger("app.video_generation")
        self._logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self._logger.handlers:
            return
        
        # Ensure logs directory exists
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # File handler - logs everything to file
        log_file = logs_dir / f"video_generation_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler - logs INFO and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)
        
        # Don't propagate to root logger
        self._logger.propagate = False
    
    @property
    def logger(self) -> logging.Logger:
        return self._logger
    
    def debug(self, msg: str, **kwargs):
        self._logger.debug(msg, **kwargs)
    
    def info(self, msg: str, **kwargs):
        self._logger.info(msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        self._logger.warning(msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        self._logger.error(msg, **kwargs)
    
    def exception(self, msg: str, **kwargs):
        """Log exception with full traceback"""
        self._logger.exception(msg, **kwargs)
    
    def step(self, step_name: str, progress: float, details: str = ""):
        """Log a video generation step"""
        pct = int(progress * 100)
        msg = f"[{pct:3d}%] {step_name}"
        if details:
            msg += f" - {details}"
        self._logger.info(msg)
    
    def step_error(self, step_name: str, error: Exception):
        """Log a step error with full traceback"""
        self._logger.error(f"❌ FAILED at step: {step_name}")
        self._logger.exception(f"Error details: {error}")
    
    def asset_loaded(self, asset_type: str, path: str, success: bool = True):
        """Log asset loading"""
        if success:
            self._logger.debug(f"✅ Loaded {asset_type}: {path}")
        else:
            self._logger.warning(f"⚠️ Failed to load {asset_type}: {path}")
    
    def video_composition_start(self, output_path: str, duration: float, aspect_ratio: str):
        """Log video composition start"""
        self._logger.info(f"🎬 Starting video composition:")
        self._logger.info(f"   Output: {output_path}")
        self._logger.info(f"   Duration: {duration:.2f}s")
        self._logger.info(f"   Aspect Ratio: {aspect_ratio}")
    
    def video_composition_complete(self, output_path: str, file_size: int):
        """Log video composition completion"""
        size_mb = file_size / (1024 * 1024) if file_size else 0
        self._logger.info(f"✅ Video composition complete!")
        self._logger.info(f"   Output: {output_path}")
        self._logger.info(f"   Size: {size_mb:.2f} MB")
    
    def generation_summary(self, video_id: str, topic: str, duration: float, success: bool, error_msg: str = ""):
        """Log generation summary"""
        self._logger.info("=" * 60)
        self._logger.info(f"VIDEO GENERATION {'COMPLETE' if success else 'FAILED'}")
        self._logger.info(f"  Video ID: {video_id}")
        self._logger.info(f"  Topic: {topic}")
        self._logger.info(f"  Duration: {duration:.2f}s")
        if not success:
            self._logger.error(f"  Error: {error_msg}")
        self._logger.info("=" * 60)


# Singleton instance
video_logger = VideoGenerationLogger()


def get_video_logger() -> VideoGenerationLogger:
    """Get the video generation logger instance"""
    return video_logger
