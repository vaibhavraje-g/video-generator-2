# backend/app/core/cloud/worker.py
"""Standalone On-Demand Worker for AWS ECS Fargate / GCP Cloud Run.

Execution Lifecycle:
1. Spun up on-demand by Lambda / Orchestrator upon SQS message arrival.
2. Initializes DB connection and fetches video generation parameters.
3. Renders video via FFmpeg / MoviePy pipeline.
4. Uploads result to Cloudflare R2 / AWS S3 with zero egress penalty.
5. Emits completion event to AWS SNS.
6. Cleanly terminates immediately (0 idle cost!).
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add backend root to path if running standalone
backend_root = Path(__file__).resolve().parent.parent.parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.core.config import settings
from app.db import MongoDB
from app.services.video_service import VideoService
from app.core.cloud.storage import storage_manager
from app.core.cloud.events import event_bus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Worker] %(message)s",
)
logger = logging.getLogger("worker")


async def run_worker():
    """Main worker task routine."""
    video_id = os.environ.get("VIDEO_JOB_ID") or (sys.argv[1] if len(sys.argv) > 1 else None)
    
    if not video_id:
        logger.error("No VIDEO_JOB_ID provided. Exiting.")
        sys.exit(1)

    logger.info(f"🚀 Worker starting for video ID: {video_id}")

    # 1. Connect to Database
    await MongoDB.connect_db()
    settings.ensure_directories()

    try:
        # 2. Run video generation
        service = VideoService()
        logger.info(f"Beginning FFmpeg generation pipeline for video {video_id}...")
        video = await service.generate_video(video_id)

        # 3. Cloud upload to S3/R2 if cloud storage is configured
        if video.file_path and Path(video.file_path).exists():
            cloud_url = await storage_manager.upload_video(video.file_path)
            logger.info(f"✅ Video uploaded to storage: {cloud_url}")
            
            # Emit completion through event bus
            await event_bus.emit_progress(
                video_id=video_id,
                status="completed",
                progress=100.0,
                current_step="Complete",
                video_url=cloud_url,
            )

        logger.info(f"🎉 Job {video_id} completed successfully. Shutting down worker.")
        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Worker job failed: {e}", exc_info=True)
        await event_bus.emit_progress(
            video_id=video_id,
            status="failed",
            progress=0,
            current_step="Failed",
            error_message=str(e),
        )
        sys.exit(1)
    finally:
        await MongoDB.close_db()


if __name__ == "__main__":
    asyncio.run(run_worker())
