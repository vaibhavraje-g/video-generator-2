# backend/app/websocket/manager.py
"""WebSocket connection manager for real-time video progress updates"""

from typing import Dict
from fastapi import WebSocket
import json


class ConnectionManager:
    """Manage WebSocket connections for video progress updates"""
    
    def __init__(self):
        # Map video_id to list of connected websockets
        self.active_connections: Dict[str, list[WebSocket]] = {}
    
    async def connect(self, video_id: str, websocket: WebSocket):
        """Accept a new WebSocket connection for a video"""
        await websocket.accept()
        if video_id not in self.active_connections:
            self.active_connections[video_id] = []
        self.active_connections[video_id].append(websocket)
    
    def disconnect(self, video_id: str, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if video_id in self.active_connections:
            if websocket in self.active_connections[video_id]:
                self.active_connections[video_id].remove(websocket)
            if not self.active_connections[video_id]:
                del self.active_connections[video_id]
    
    async def broadcast(self, video_id: str, data: dict):
        """Broadcast progress update to all connections watching a video"""
        if video_id in self.active_connections:
            message = json.dumps(data)
            dead_connections = []
            
            for websocket in self.active_connections[video_id]:
                try:
                    await websocket.send_text(message)
                except Exception:
                    dead_connections.append(websocket)
            
            # Clean up dead connections
            for ws in dead_connections:
                self.disconnect(video_id, ws)
    
    async def send_progress(
        self, 
        video_id: str, 
        status: str, 
        progress: float, 
        current_step: str,
        video_url: str | None = None,
        error_message: str | None = None
    ):
        """Send a progress update message"""
        await self.broadcast(video_id, {
            "type": "progress",
            "video_id": video_id,
            "status": status,
            "progress": progress,
            "current_step": current_step,
            "video_url": video_url,
            "error_message": error_message
        })
