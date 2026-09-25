# backend/app/api/v1/routes/videos.py
"""Video generation routes"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal

from app.services.video_service import VideoService
from app.models import VideoResponse, VideoStatus, User, VideoConfigModel
from app.middleware import get_current_active_user
from app.generators import GeneratorRegistry
from app.websocket import connection_manager

router = APIRouter(prefix="/videos", tags=["videos"])

# Thread pool for CPU-bound video generation tasks
# This prevents blocking the async event loop during moviepy operations
_video_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="video_gen")


class VideoGenerateRequest(BaseModel):
    """Video generation request"""
    project_id: str
    generator_id: str = "family_guy"
    topic: str
    
    # Common video config
    aspect_ratio: Literal["9:16", "1:1", "16:9"] = "9:16"
    duration: Literal["short", "long"] = "short"
    output_format: Literal["mp4", "webm", "mov"] = "mp4"
    quality: Literal["720p", "1080p", "4k"] = "1080p"
    
    # Generator-specific config
    generator_config: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=VideoResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_video(
    request: VideoGenerateRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a video (async background task)
    
    Returns:
        Video record with pending status
    """
    # Validate generator exists
    if not GeneratorRegistry.is_registered(request.generator_id):
        available = GeneratorRegistry.list_ids()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Generator '{request.generator_id}' not found. Available: {available}"
        )
    
    # Check duration support
    generator = GeneratorRegistry.get(request.generator_id)
    supported = [d.value for d in generator.supported_durations]
    if request.duration not in supported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Generator '{request.generator_id}' does not support '{request.duration}' duration. Supported: {supported}"
        )
    
    video_service = VideoService()
    
    # Build video config
    video_config = VideoConfigModel(
        aspect_ratio=request.aspect_ratio,
        duration=request.duration,
        output_format=request.output_format,
        quality=request.quality
    )
    
    tenant_id = getattr(current_user, "tenant_id", None) or str(current_user.id)

    # Create video record with tenant validation
    try:
        video = await video_service.create_video_record(
            project_id=request.project_id,
            user_id=str(current_user.id),
            tenant_id=tenant_id,
            topic=request.topic,
            generator_id=request.generator_id,
            video_config=video_config.model_dump(),
            generator_config=request.generator_config or {}
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Schedule video generation in background using thread pool
    # This prevents blocking calls (moviepy) from freezing the event loop
    async def run_generation_in_thread(video_id: str):
        """Wrapper to run async video generation in a way that doesn't block"""
        loop = asyncio.get_event_loop()
        # Run the async generate_video coroutine
        # The generate_video internally uses blocking moviepy calls,
        # so we run the entire coroutine in a thread-safe manner
        try:
            await video_service.generate_video(video_id)
        except Exception as e:
            print(f"Background video generation error: {e}")
    
    background_tasks.add_task(run_generation_in_thread, str(video.id))
    
    return VideoResponse(
        _id=str(video.id),
        project_id=str(video.project_id),
        user_id=str(video.user_id),
        tenant_id=video.tenant_id,
        topic=video.topic,
        generator_id=video.generator_id,
        video_config=video.video_config,
        generator_config=video.generator_config,
        video_url=video.video_url,
        status=video.status,
        progress=video.progress,
        current_step=video.current_step,
        metadata=video.metadata,
        error_message=video.error_message,
        created_at=video.created_at,
        completed_at=video.completed_at,
    )


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get video details with tenant ownership verification
    
    Returns:
        Video information
    """
    video_service = VideoService()
    tenant_id = getattr(current_user, "tenant_id", None) or str(current_user.id)
    video = await video_service.get_video(video_id, str(current_user.id), tenant_id=tenant_id)
    
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found or access denied"
        )
    
    return VideoResponse(
        _id=str(video.id),
        project_id=str(video.project_id),
        user_id=str(video.user_id),
        tenant_id=video.tenant_id,
        topic=video.topic,
        generator_id=video.generator_id,
        video_config=video.video_config,
        generator_config=video.generator_config,
        video_url=video.video_url,
        status=video.status,
        progress=video.progress,
        current_step=video.current_step,
        metadata=video.metadata,
        error_message=video.error_message,
        created_at=video.created_at,
        completed_at=video.completed_at,
    )


@router.websocket("/{video_id}/ws")
async def websocket_video_progress(websocket: WebSocket, video_id: str):
    """
    WebSocket endpoint for real-time video generation progress
    """
    await connection_manager.connect(video_id, websocket)
    try:
        await websocket.send_json({
            "type": "connected",
            "video_id": video_id,
            "message": "Connected to video progress stream"
        })
        while True:
            try:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error for video {video_id}: {e}")
    finally:
        connection_manager.disconnect(video_id, websocket)


@router.get("/{video_id}/stream")
async def stream_video_progress(request: Request, video_id: str):
    """
    Server-Sent Events (SSE) streaming endpoint for video generation progress.
    Firewall-friendly, auto-reconnecting HTTP event stream.
    """
    import json
    from fastapi.responses import StreamingResponse

    q = connection_manager.subscribe_sse(video_id)

    async def sse_event_generator():
        try:
            # Send initial confirmation event
            yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'video_id': video_id})}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Await new progress message with a 15-second heartbeat
                    data = await asyncio.wait_for(q.get(), timeout=15.0)
                    status_val = data.get("status", "processing")
                    event_type = "complete" if status_val == "completed" else ("error" if status_val == "failed" else "progress")
                    yield f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
                    if status_val in ("completed", "failed"):
                        break
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep HTTP connection alive
                    yield ": keep-alive\n\n"
        finally:
            connection_manager.unsubscribe_sse(video_id, q)

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
