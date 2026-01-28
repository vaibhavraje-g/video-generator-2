# backend/tests/integration/test_video_generation.py
"""End-to-end integration tests for video generation"""

import pytest
from pathlib import Path
from httpx import AsyncClient

from app.main import app
from app.services.video_service import VideoService
from app.services.project_service import ProjectService
from app.models import ProjectCreate


@pytest.mark.asyncio
async def test_video_generation_flow(test_db, test_user_tokens, valid_project_data):
    """Test complete video generation flow from API request to completion"""
    user, tokens = test_user_tokens
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Create a project
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
        
        assert generate_response.status_code == 202  # Accepted
        video_data = generate_response.json()
        assert video_data["status"] == "pending"
        assert video_data["topic"] == video_request["topic"]
        video_id = video_data["_id"]
        
        # 3. Check video status
        status_response = await client.get(
            f"/api/v1/videos/{video_id}",
            headers={"Authorization": f"Bearer {tokens['access_token']}"}
        )
        assert status_response.status_code == 200
        video = status_response.json()
        assert video["_id"] == video_id


@pytest.mark.asyncio
async def test_video_service_generate_video_record(test_db, test_user, valid_project_data):
    """Test video service creates video record correctly"""
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
        topic="Test topic",
        generator_id="family_guy",
        video_config={
            "aspect_ratio": "9:16",
            "duration": "short",
            "output_format": "mp4",
            "quality": "1080p"
        }
    )
    
    assert video.topic == "Test topic"
    assert video.generator_id == "family_guy"
    assert video.status.value == "pending"
    assert video.progress == 0


@pytest.mark.asyncio
async def test_video_generation_error_handling(test_db, test_user_tokens, valid_project_data):
    """Test that video generation errors are properly handled"""
    user, tokens = test_user_tokens
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create project
        project_response = await client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json=valid_project_data
        )
        project_id = project_response.json()["_id"]
        
        # Try to generate with invalid generator
        video_request = {
            "project_id": project_id,
            "generator_id": "invalid_generator",
            "topic": "Test",
            "aspect_ratio": "9:16",
            "duration": "short",
            "output_format": "mp4",
            "quality": "1080p"
        }
        
        response = await client.post(
            "/api/v1/videos/generate",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
            json=video_request
        )
        
        assert response.status_code == 400
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_video_status_updates(test_db, test_user, valid_project_data):
    """Test video status updates during generation"""
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
        topic="Test",
        generator_id="family_guy"
    )
    
    # Update status
    await video_service.update_video_status(
        str(video.id),
        status="processing",
        progress=50,
        current_step="Generating audio"
    )
    
    # Verify update
    updated_video = await video_service.get_video(str(video.id), str(user.id))
    assert updated_video.status.value == "processing"
    assert updated_video.progress == 50
    assert updated_video.current_step == "Generating audio"

