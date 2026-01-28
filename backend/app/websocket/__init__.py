# backend/app/websocket/__init__.py
"""WebSocket module for real-time updates"""

from .manager import ConnectionManager

connection_manager = ConnectionManager()

__all__ = ["connection_manager", "ConnectionManager"]
