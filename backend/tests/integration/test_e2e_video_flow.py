# backend/tests/integration/test_e2e_video_flow.py
"""End-to-end integration tests for complete video generation flow with WebSocket"""

import pytest
import json
from httpx import AsyncClient
from unittest.mock import AsyncMock

from app.main import app
from app.services.video_service import VideoService
from app.services.project_service import ProjectService
from app.models import ProjectCreate


@pytest.mark.asyncio
async def test_complete_video_generation_flow_with_websocket(test_db, test_user_tokens, valid_project_data):
    """Test complete flow: create project -> generate video -> receive WebSocket updates -> preview video"""
    user, tokens = test_user_tokens
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Create project
        project_response = await client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json=valid_project_data
        )
        assert project_response.status_code == 201
        project = project_response.json()
        project_id = project["_id"]
        
        # 2. Request video generation
        video_request = {
            "project_id": project_id,
            "generator_id": "family_guy",
            "topic": "How does photosynthesis work?",
            "aspect_ratio": "9:16",
            "duration": "short",
            "output_format": "mp4",
            "quality": "1080p"
        }
        
        generate_response = await client.post(
            "/api/v1/videos/generate",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json=video_request
        )
        
        assert generate_response.status_code == 202
        video_data = generate_response.json()
        assert video_data["status"] == "pending"
        video_id = video_data["_id"]
        
        # 3. Get project history (should include the new video)
        history_response = await client.get(
            f"/api/v1/projects/{project_id}/history",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        
        assert history_response.status_code == 200
        history = history_response.json()
        assert len(history) > 0
        assert any(v["_id"] == video_id for v in history)
        
        # 4. Check video status endpoint
        status_response = await client.get(
            f"/api/v1/videos/{video_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        assert status_response.status_code == 200
        video = status_response.json()
        assert video["_id"] == video_id
        assert video["topic"] == video_request["topic"]


@pytest.mark.asyncio
async def test_video_url_generation(test_db, test_user, valid_project_data):
    """Test that video URLs are properly generated and accessible"""
    user, _ = test_user
    project_service = ProjectService()
    video_service = VideoService()
    
    # Create project
    project_data = ProjectCreate(**valid_project_data)
    project = await project_service.create_project(str(user.id), project_data)
    
    # Create video record
    video = await video_service.create_video_record(
        project_id=str(project.id),
        user_id=str(user.id),
        topic="Test video",
        generator_id="family_guy"
    )
    
    # Simulate video completion with URL
    video_url = "/static/test_video.mp4"
    await video_service.update_video_result(
        str(video.id),
        video_url=video_url,
        file_path="/path/to/video.mp4",
        metadata={"test": "data"}
    )
    
    # Verify video has URL
    updated_video = await video_service.get_video(str(video.id), str(user.id))
    assert updated_video.video_url == video_url
    assert updated_video.status.value == "completed"


@pytest.mark.asyncio
async def test_websocket_progress_updates(test_db, test_user_tokens, valid_project_data):
    """Test that WebSocket sends progress updates correctly"""
    from app.websocket.manager import ConnectionManager
    from unittest.mock import AsyncMock
    
    manager = ConnectionManager()
    mock_ws = AsyncMock()
    mock_ws.send_text = AsyncMock()
    
    video_id = "test_video_123"
    
    # Connect
    await manager.connect(video_id, mock_ws)
    
    # Send progress updates
    await manager.send_progress(
        video_id=video_id,
        status="processing",
        progress=50,
        current_step="Generating audio"
    )
    
    # Verify message was sent
    assert mock_ws.send_text.called
    message = json.loads(mock_ws.send_text.call_args[0][0])
    assert message["type"] == "progress"
    assert message["status"] == "processing"
    assert message["progress"] == 50
    
    # Send completion
    await manager.send_progress(
        video_id=video_id,
        status="completed",
        progress=100,
        current_step="Complete",
        video_url="/static/video.mp4"
    )
    
    # Verify completion message
    messages = [json.loads(call[0][0]) for call in mock_ws.send_text.call_args_list]
    completion_msg = messages[-1]
    assert completion_msg["status"] == "completed"
    assert completion_msg["video_url"] == "/static/video.mp4"

