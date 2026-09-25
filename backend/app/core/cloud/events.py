# backend/app/core/cloud/events.py
"""Unified Event Bus supporting WebSockets and AWS SNS Topic Fan-out.

Enables decoupled asynchronous communication:
Worker completes FFmpeg render -> Publishes event to AWS SNS ->
1) Fan-out to Backend Webhook / Lambda to record COMPLETED in DB
2) Real-time push via WebSocket / SSE to the frontend client.
"""

import json
import logging
from typing import Any, Dict, Optional
from app.core.config import settings
from app.websocket import connection_manager

logger = logging.getLogger("app.cloud.events")


class EventBusManager:
    """Dispatches video generation events across WebSockets and AWS SNS."""

    def __init__(self):
        self.sns_topic_arn = settings.SNS_TOPIC_ARN
        self.region = settings.AWS_REGION
        self._sns_client = None

    def _get_sns_client(self):
        if self._sns_client is None:
            try:
                import boto3
                self._sns_client = boto3.client("sns", region_name=self.region)
            except ImportError:
                pass
        return self._sns_client

    async def emit_progress(
        self,
        video_id: str,
        status: str,
        progress: float,
        current_step: str,
        video_url: Optional[str] = None,
        error_message: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ):
        """Emits progress event to both WebSocket client and SNS topic."""
        # 1. Real-time WebSocket delivery
        try:
            await connection_manager.send_progress(
                video_id=video_id,
                status=status,
                progress=progress,
                current_step=current_step,
                video_url=video_url,
                error_message=error_message,
            )
        except Exception as ws_err:
            logger.debug(f"WebSocket send note: {ws_err}")

        # 2. AWS SNS Topic Fan-out (if configured)
        if self.sns_topic_arn:
            sns = self._get_sns_client()
            if sns:
                try:
                    payload = {
                        "event": "video.progress" if status == "processing" else f"video.{status}",
                        "video_id": video_id,
                        "status": status,
                        "progress": progress,
                        "current_step": current_step,
                        "video_url": video_url,
                        "error_message": error_message,
                        "metadata": extra_data or {},
                    }
                    sns.publish(
                        TopicArn=self.sns_topic_arn,
                        Message=json.dumps(payload),
                        Subject=f"VideoGen: {status.upper()} - {video_id[:8]}",
                        MessageAttributes={
                            "status": {
                                "DataType": "String",
                                "StringValue": status,
                            },
                            "event_type": {
                                "DataType": "String",
                                "StringValue": "video_status_change",
                            },
                        },
                    )
                    logger.info(f"Published status '{status}' to SNS topic {self.sns_topic_arn}")
                except Exception as sns_err:
                    logger.error(f"Failed to publish to SNS topic: {sns_err}")


event_bus = EventBusManager()
