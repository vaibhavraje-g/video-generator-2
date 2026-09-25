# backend/app/services/video_service.py
"""Video generation service with database integration"""

from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import uuid
from bson import ObjectId

from app.db import get_database
from app.models import Video, VideoStatus
from app.generators import GeneratorRegistry
from app.generators.base import VideoConfig, AspectRatio, VideoDuration, OutputFormat, VideoQuality
from app.core.config import settings
from app.websocket import connection_manager
from app.middleware.security import sanitize_text_input, validate_safe_url

# Placeholder ObjectId for dev mode bypass (strictly restricted to development)
DEV_USER_OBJECT_ID = ObjectId("000000000000000000000001")


def _get_oid(id_str: str) -> ObjectId:
    """Safely convert string ID to ObjectId, strictly gating dev mode."""
    if id_str == "dev_user_id":
        if settings.ENVIRONMENT != "development" and not settings.DEBUG:
            raise ValueError("Development user bypass is disabled in production")
        return DEV_USER_OBJECT_ID
    if not ObjectId.is_valid(id_str):
        raise ValueError(f"Invalid ObjectId format: {id_str}")
    return ObjectId(id_str)


class VideoService:
    """Service for video generation and management"""
    
    def __init__(self):
        self.db = get_database()
        self.videos_collection = self.db.videos
    
    async def create_video_record(
        self, 
        project_id: str, 
        user_id: str, 
        topic: str, 
        generator_id: str = "family_guy",
        video_config: Optional[Dict[str, Any]] = None,
        generator_config: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None
    ) -> Video:
        """
        Create a video record in the database with sanitized topic input and multi-tenant validation.
        """
        clean_topic = sanitize_text_input(topic)
        if not clean_topic:
            raise ValueError("Video topic cannot be empty after sanitization")

        active_tenant = tenant_id or user_id
        project_oid = _get_oid(project_id)
        user_oid = _get_oid(user_id)

        # Multi-tenant cross-boundary guard: Verify project ownership for tenant
        project = await self.db.projects.find_one({
            "_id": project_oid,
            "$or": [{"tenant_id": active_tenant}, {"user_id": user_oid}]
        })
        if not project:
            raise ValueError(f"Project '{project_id}' not found or access denied for tenant")

        # Validate custom background URL if provided (SSRF guard)
        gen_cfg = generator_config or {}
        if gen_cfg.get("background") == "custom" and gen_cfg.get("background_url"):
            validate_safe_url(gen_cfg["background_url"])

        video_dict = {
            "project_id": project_oid,
            "user_id": user_oid,
            "tenant_id": active_tenant,
            "topic": clean_topic,
            "generator_id": generator_id,
            "video_config": video_config or {},
            "generator_config": gen_cfg,
            "status": VideoStatus.PENDING,
            "progress": 0,
            "current_step": "Queued",
            "created_at": datetime.utcnow(),
        }
        
        result = await self.videos_collection.insert_one(video_dict)
        
        # Convert ObjectIds to strings for Pydantic model
        video_dict["_id"] = str(result.inserted_id)
        video_dict["project_id"] = str(video_dict["project_id"])
        video_dict["user_id"] = str(video_dict["user_id"])
        video_dict["tenant_id"] = active_tenant
        
        return Video(**video_dict)
    
    async def update_video_status(
        self, 
        video_id: str, 
        status: VideoStatus, 
        progress: Optional[float] = None,
        current_step: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Update video status and progress"""
        update_data = {"status": status}
        
        if progress is not None:
            update_data["progress"] = progress
        
        if current_step is not None:
            update_data["current_step"] = current_step
        
        if status == VideoStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
            update_data["progress"] = 100
        
        if error_message:
            update_data["error_message"] = error_message
        
        await self.videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": update_data}
        )
    
    async def update_video_result(
        self, 
        video_id: str, 
        video_url: str, 
        file_path: str,
        metadata: dict
    ):
        """Update video with generation results"""
        await self.videos_collection.update_one(
            {"_id": ObjectId(video_id)},
            {"$set": {
                "video_url": video_url,
                "file_path": file_path,
                "metadata": metadata,
                "status": VideoStatus.COMPLETED,
                "progress": 100,
                "current_step": "Complete",
                "completed_at": datetime.utcnow(),
            }}
        )
    
    def _convert_video_dict(self, video_dict: dict) -> dict:
        """Convert ObjectIds to strings for Pydantic compatibility"""
        video_dict["_id"] = str(video_dict["_id"])
        video_dict["project_id"] = str(video_dict["project_id"])
        video_dict["user_id"] = str(video_dict["user_id"])
        if "tenant_id" not in video_dict or not video_dict["tenant_id"]:
            video_dict["tenant_id"] = str(video_dict["user_id"])
        return video_dict
    
    async def generate_video(self, video_id: str) -> Video:
        """Generate a video using the appropriate generator"""
        video_dict = await self.videos_collection.find_one({"_id": ObjectId(video_id)})
        if not video_dict:
            raise ValueError("Video not found")
        
        video = Video(**self._convert_video_dict(video_dict.copy()))
        
        try:
            await self.update_video_status(
                video_id, 
                VideoStatus.PROCESSING,
                progress=5,
                current_step="Initializing generator"
            )
            
            generator = GeneratorRegistry.get(video.generator_id)
            
            # video_config might be a dict or Pydantic model
            vc = video.video_config or {}
            if hasattr(vc, 'model_dump'):
                vc = vc.model_dump()
            elif hasattr(vc, 'dict'):
                vc = vc.dict()
            
            video_config = VideoConfig(
                aspect_ratio=AspectRatio(vc.get("aspect_ratio", "9:16")),
                duration=VideoDuration(vc.get("duration", "short")),
                output_format=OutputFormat(vc.get("output_format", "mp4")),
                quality=VideoQuality(vc.get("quality", "1080p"))
            )
            
            # Use static directory for serving videos
            static_dir = Path(__file__).parent.parent / "static"
            static_dir.mkdir(parents=True, exist_ok=True)
            output_filename = f"{video.generator_id}_{uuid.uuid4().hex[:8]}.{video_config.output_format}"
            output_path = str(static_dir / output_filename)
            
            async def progress_callback(step: str, progress: float):
                progress_pct = progress * 100
                await self.update_video_status(
                    video_id,
                    VideoStatus.PROCESSING,
                    progress=progress_pct,
                    current_step=step
                )
                # Broadcast via WebSocket
                await connection_manager.send_progress(
                    video_id=video_id,
                    status="processing",
                    progress=progress_pct,
                    current_step=step
                )
            
            result = await generator.generate(
                topic=video.topic,
                video_config=video_config,
                generator_config=video.generator_config or {},
                output_path=output_path,
                progress_callback=progress_callback
            )
            
            # Use full URL path for frontend
            video_url = f"/static/{output_filename}"
            
            # Update database first
            await self.update_video_result(
                video_id,
                video_url=video_url,
                file_path=result.output_path,
                metadata={
                    "topic": video.topic,
                    "duration_seconds": result.duration_seconds,
                    "file_size_bytes": result.file_size_bytes,
                    **result.metadata
                }
            )
            
            # Broadcast completion via WebSocket with full video details
            try:
                await connection_manager.send_progress(
                    video_id=video_id,
                    status="completed",
                    progress=100,
                    current_step="Complete",
                    video_url=video_url
                )
            except Exception as ws_error:
                print(f"Warning: Failed to send WebSocket completion message: {ws_error}")
            
            video_dict = await self.videos_collection.find_one({"_id": ObjectId(video_id)})
            return Video(**self._convert_video_dict(video_dict.copy()))
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            error_msg = f"{str(e)}\n{error_trace}"
            
            await self.update_video_status(
                video_id, 
                VideoStatus.FAILED, 
                progress=0,
                current_step="Failed",
                error_message=str(e)
            )
            # Broadcast failure via WebSocket
            try:
                await connection_manager.send_progress(
                    video_id=video_id,
                    status="failed",
                    progress=0,
                    current_step="Failed",
                    error_message=str(e)
                )
            except Exception as ws_error:
                print(f"Failed to send WebSocket error message: {ws_error}")
            
            # Log the full error for debugging
            print(f"❌ Video generation failed for {video_id}: {error_msg}")
            raise
    
    async def get_video(self, video_id: str, user_id: str, tenant_id: Optional[str] = None) -> Optional[Video]:
        """Get a video with tenant ownership verification"""
        if not ObjectId.is_valid(video_id):
            return None
        
        user_oid = _get_oid(user_id)
        if tenant_id:
            query = {
                "_id": ObjectId(video_id),
                "$or": [
                    {"tenant_id": tenant_id},
                    {"tenant_id": {"$exists": False}, "user_id": user_oid}
                ]
            }
        else:
            query = {"_id": ObjectId(video_id), "user_id": user_oid}
        
        video_dict = await self.videos_collection.find_one(query)
        if not video_dict:
            return None
        
        return Video(**self._convert_video_dict(video_dict.copy()))
