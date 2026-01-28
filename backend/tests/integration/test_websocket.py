# backend/tests/integration/test_websocket.py
"""Integration tests for WebSocket video progress updates"""

import pytest
import json
from unittest.mock import AsyncMock

from app.websocket.manager import ConnectionManager
from fastapi import WebSocket


@pytest.mark.asyncio
async def test_websocket_connection_manager():
    """Test WebSocket connection manager basic functionality"""
    manager = ConnectionManager()
    
    # Create a mock WebSocket
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.send_text = AsyncMock()
    
    # Test connection
    await manager.connect("test_video_id", mock_ws)
    assert "test_video_id" in manager.active_connections
    assert len(manager.active_connections["test_video_id"]) == 1
    
    # Test broadcast
    await manager.send_progress(
        video_id="test_video_id",
        status="processing",
        progress=50,
        current_step="Generating audio"
    )
    
    # Verify message was sent
    assert mock_ws.send_text.called
    call_args = mock_ws.send_text.call_args[0][0]
    data = json.loads(call_args)
    assert data["type"] == "progress"
    assert data["video_id"] == "test_video_id"
    assert data["status"] == "processing"
    assert data["progress"] == 50
    
    # Test disconnect
    manager.disconnect("test_video_id", mock_ws)
    assert "test_video_id" not in manager.active_connections


@pytest.mark.asyncio
async def test_websocket_multiple_connections():
    """Test WebSocket with multiple connections to same video"""
    manager = ConnectionManager()
    
    mock_ws1 = AsyncMock(spec=WebSocket)
    mock_ws1.send_text = AsyncMock()
    mock_ws2 = AsyncMock(spec=WebSocket)
    mock_ws2.send_text = AsyncMock()
    
    await manager.connect("video_1", mock_ws1)
    await manager.connect("video_1", mock_ws2)
    
    assert len(manager.active_connections["video_1"]) == 2
    
    # Broadcast should send to both
    await manager.send_progress(
        video_id="video_1",
        status="processing",
        progress=75,
        current_step="Rendering"
    )
    
    assert mock_ws1.send_text.called
    assert mock_ws2.send_text.called


@pytest.mark.asyncio
async def test_websocket_dead_connection_cleanup():
    """Test that dead WebSocket connections are cleaned up"""
    manager = ConnectionManager()
    
    mock_ws = AsyncMock(spec=WebSocket)
    mock_ws.send_text = AsyncMock(side_effect=Exception("Connection closed"))
    
    await manager.connect("video_1", mock_ws)
    
    # Try to broadcast - should handle error and cleanup
    await manager.send_progress(
        video_id="video_1",
        status="processing",
        progress=50,
        current_step="Processing"
    )
    
    # Connection should be removed
    assert "video_1" not in manager.active_connections

