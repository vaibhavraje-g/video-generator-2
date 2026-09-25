# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Dict


class Settings(BaseSettings):
    # --- Core API & Environment ---
    ENVIRONMENT: str = "development"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "http://localhost:3000",
        "https://*.vercel.app"
    ]

    # --- Database ---
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "video_generator"

    # --- Authentication & Security ---
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENABLE_RATE_LIMITING: bool = True

    # --- Cloud Architecture & 0-Cost Pipeline ---
    STORAGE_BACKEND: str = "local"  # "local", "s3", or "r2"
    S3_BUCKET_NAME: str = ""
    S3_ENDPOINT_URL: str | None = None  # Cloudflare R2 endpoint URL
    AWS_REGION: str = "us-east-1"
    QUEUE_BACKEND: str = "local"  # "local" (in-memory async) or "sqs"
    SQS_QUEUE_URL: str = ""
    SNS_TOPIC_ARN: str = ""
    ECS_CLUSTER_NAME: str = ""
    ECS_TASK_DEFINITION: str = ""
    ECS_SUBNET_IDS: list[str] = []

    # --- API Keys & Multi-Model Providers ---
    GEMINI_API_KEY: str | None = None
    PIXABAY_API_KEY: str | None = None
    META_API_KEY: str | None = None
    META_API_BASE: str = "https://api.meta.ai/v1"
    GROQ_API_KEY: str | None = None

    # --- LLM Config ---
    GEMINI_MODEL: str = "gemini-2.5-flash"
    PRIMARY_LLM_PROVIDER: str = "auto"  # "auto", "meta_muse", "gemini", "groq"

    # --- Video backend ---
    COMPOSE_BACKEND: str = "moviepy"  # or "ffmpeg"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

    # LLM config
    MAX_LLM_RETRIES: int = 3
    RETRY_DELAY: float = 1.5
    TEMPERATURE: float = 0.7
    MAX_OUTPUT_TOKENS: int = 2048
    TOP_P: float = 0.9
    TOP_K: int = 40

    SAFETY_SETTINGS: Dict[str, str] = {
        "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
        "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
    }

    # --- Project paths ---
    PROJECTS_DIR: str = "projects"
    ASSETS_DIR: str = "assets"
    CHARACTERS_DIR: str = "assets/characters"
    VIDEOS_DIR: str = "assets/videos"
    TEMP_DIR: str = "assets/temp"
    OUTPUT_DIR: str = "assets/output"

    # --- Audio settings ---
    TTS_LANGUAGE: str = "en"
    AUDIO_FORMAT: str = "mp3"
    AUDIO_CODEC: str = "aac"

    # --- Video settings ---
    VIDEO_FPS: int = 24
    VIDEO_CODEC: str = "libx264"

    # --- Character positions ---
    CHARACTER_POSITIONS: Dict[str, str] = {
        "peter": "left",
        "stewie": "right",
        "default": "center",
    }

    # --- Text styling ---
    SUBTITLE_CONFIG: Dict[str, str | int | float] = {
        "fontsize": 95,
        "color": "yellow",
        "font": "DejaVu-Sans-Bold",
        "stroke_color": "black",
        "stroke_width": 0.3,
    }

    TITLE_CONFIG: Dict[str, str | int] = {
        "fontsize": 60,
        "color": "white",
        "font": "Arial-Bold",
        "bg_color": "black",
    }

    @staticmethod
    def ensure_directories():
        """Create all necessary directories if they don't exist"""
        import os

        directories = [
            settings.ASSETS_DIR,
            settings.CHARACTERS_DIR,
            settings.VIDEOS_DIR,
            settings.TEMP_DIR,
            settings.OUTPUT_DIR,
            settings.PROJECTS_DIR,
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


settings = Settings()
