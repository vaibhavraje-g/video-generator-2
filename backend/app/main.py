# backend/app/main.py
"""Main FastAPI application"""

# Apply compatibility patches FIRST (before moviepy is imported)
import app.core.compat  # noqa: F401

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db import MongoDB
from app.api import api_router
from app.middleware.exception_handlers import setup_exception_handlers


def setup_file_logging():
    """Configure file-based logging"""
    # Create logs directory
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    # Setup logging format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # File handler for all app logs
    file_handler = logging.FileHandler(logs_dir / "app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    # Error-only file handler
    error_handler = logging.FileHandler(logs_dir / "errors.log", encoding="utf-8")
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    
    # Configure app logger
    app_logger = logging.getLogger("app")
    app_logger.setLevel(logging.INFO)
    
    return app_logger


# Setup logging on module load
logger = setup_file_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting application...")
    print("🚀 Starting application...")
    
    # Connect to MongoDB
    await MongoDB.connect_db()
    
    # Ensure directories exist
    settings.ensure_directories()
    
    logger.info("✅ Application started successfully")
    print("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")
    print("🛑 Shutting down application...")
    await MongoDB.close_db()
    logger.info("👋 Application shutdown complete")
    print("👋 Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="Video Generator API",
    description="Full-stack video generation platform with authentication and project management",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup global exception handlers
setup_exception_handlers(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Mount static files for serving generated videos
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Video Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = await MongoDB.check_health()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "database": "connected" if db_healthy else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

