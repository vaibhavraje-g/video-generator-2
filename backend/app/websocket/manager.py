# backend/app/websocket/manager.py
"""Connection manager supporting both WebSockets and Server-Sent Events (SSE)."""

import asyncio
import json
from typing import Dict, List, Optional
from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSockets and Server-Sent Events (SSE) subscriptions for real-time video progress."""
    
    def __init__(self):
        # Map video_id to list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Map video_id to list of active SSE subscriber asyncio.Queues
        self.sse_subscribers: Dict[str, List[asyncio.Queue]] = {}
    
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
                
    def subscribe_sse(self, video_id: str) -> asyncio.Queue:
        """Subscribe to Server-Sent Events for a video_id, returning an event queue."""
        q: asyncio.Queue = asyncio.Queue()
        if video_id not in self.sse_subscribers:
            self.sse_subscribers[video_id] = []
        self.sse_subscribers[video_id].append(q)
        return q

    def unsubscribe_sse(self, video_id: str, q: asyncio.Queue):
        """Unsubscribe and clean up an SSE event queue."""
        if video_id in self.sse_subscribers:
            if q in self.sse_subscribers[video_id]:
                self.sse_subscribers[video_id].remove(q)
            if not self.sse_subscribers[video_id]:
                del self.sse_subscribers[video_id]
    
    async def broadcast(self, video_id: str, data: dict):
        """Broadcast progress update to all WebSocket and SSE connections watching a video."""
        message = json.dumps(data)
        
        # 1. Deliver to WebSockets
        if video_id in self.active_connections:
            dead_connections = []
            for websocket in self.active_connections[video_id]:
                try:
                    await websocket.send_text(message)
                except Exception:
                    dead_connections.append(websocket)
            for ws in dead_connections:
                self.disconnect(video_id, ws)

        # 2. Deliver to SSE subscriber queues
        if video_id in self.sse_subscribers:
            for q in self.sse_subscribers[video_id]:
                try:
                    await q.put(data)
                except Exception:
                    pass
    
    async def send_progress(
        self, 
        video_id: str, 
        status: str, 
        progress: float, 
        current_step: str,
        video_url: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        """Send a progress update message across all real-time channels."""
        await self.broadcast(video_id, {
            "type": "progress",
            "video_id": video_id,
            "status": status,
            "progress": progress,
            "current_step": current_step,
            "video_url": video_url,
            "error_message": error_message
        })


connection_manager = ConnectionManager()
