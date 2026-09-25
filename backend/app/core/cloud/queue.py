# backend/app/core/cloud/queue.py
"""Unified Job Queue Manager supporting Local Async Execution and AWS SQS.

Architecture:
Frontend/API -> Enqueues Job -> SQS FIFO (with Dead-Letter-Queue DLQ)
-> Triggers Lambda Orchestrator or ECS Fargate Spot / Cloud Run Job
-> Worker runs FFmpeg container -> Turns off on completion ($0 Idle Cost!).
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger("app.cloud.queue")


class JobQueueManager:
    """Manages video generation job dispatching via Local Async or AWS SQS."""

    def __init__(self):
        self.backend = settings.QUEUE_BACKEND.lower()
        self.sqs_queue_url = settings.SQS_QUEUE_URL
        self.region = settings.AWS_REGION
        self._sqs_client = None
        self._ecs_client = None

    def _get_sqs_client(self):
        if self._sqs_client is None:
            try:
                import boto3
                self._sqs_client = boto3.client("sqs", region_name=self.region)
            except ImportError:
                logger.warning("boto3 not found. Defaulting to local queue.")
                self.backend = "local"
        return self._sqs_client

    def _get_ecs_client(self):
        if self._ecs_client is None:
            try:
                import boto3
                self._ecs_client = boto3.client("ecs", region_name=self.region)
            except ImportError:
                pass
        return self._ecs_client

    async def enqueue_video_generation(
        self,
        video_id: str,
        project_id: str,
        user_id: str,
        topic: str,
        generator_id: str,
        video_config: Dict[str, Any],
        generator_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Dispatches video generation task to AWS SQS or local async runner."""
        payload = {
            "job_id": str(uuid.uuid4()),
            "video_id": video_id,
            "project_id": project_id,
            "user_id": user_id,
            "topic": topic,
            "generator_id": generator_id,
            "video_config": video_config,
            "generator_config": generator_config,
        }

        if self.backend == "sqs" and self.sqs_queue_url:
            sqs = self._get_sqs_client()
            if sqs:
                try:
                    logger.info(f"Sending video job {video_id} to SQS queue {self.sqs_queue_url}")
                    # SQS FIFO requires MessageGroupId and MessageDeduplicationId
                    response = sqs.send_message(
                        QueueUrl=self.sqs_queue_url,
                        MessageBody=json.dumps(payload),
                        MessageGroupId="video-generation",
                        MessageDeduplicationId=f"{video_id}_{uuid.uuid4().hex[:8]}",
                    )
                    
                    # Optionally launch on-demand ECS Fargate task if configured
                    if settings.ECS_CLUSTER_NAME and settings.ECS_TASK_DEFINITION:
                        await self.trigger_ecs_fargate_task(video_id)

                    return {
                        "status": "queued",
                        "queue": "sqs",
                        "message_id": response.get("MessageId"),
                    }
                except Exception as e:
                    logger.error(f"Failed to enqueue to SQS: {e}. Falling back to local execution.")

        # Local background task execution
        logger.info(f"Dispatching video job {video_id} locally in background")
        from app.services.video_service import VideoService
        video_service = VideoService()
        asyncio.create_task(video_service.generate_video(video_id))

        return {
            "status": "queued",
            "queue": "local",
            "job_id": payload["job_id"],
        }

    async def trigger_ecs_fargate_task(self, video_id: str) -> Optional[str]:
        """Spins up an ephemeral ECS Fargate Spot task to render FFmpeg.

        Terminates automatically when finished, costing $0 while idle.
        """
        ecs = self._get_ecs_client()
        if not ecs:
            return None

        try:
            logger.info(f"Spinning up on-demand ECS Fargate task for video {video_id}")
            run_params = {
                "cluster": settings.ECS_CLUSTER_NAME,
                "taskDefinition": settings.ECS_TASK_DEFINITION,
                "launchType": "FARGATE",
                "count": 1,
                "platformVersion": "LATEST",
                "networkConfiguration": {
                    "awsvpcConfiguration": {
                        "subnets": settings.ECS_SUBNET_IDS,
                        "assignPublicIp": "ENABLED",
                    }
                },
                "overrides": {
                    "containerOverrides": [
                        {
                            "name": "video-renderer",
                            "environment": [
                                {"name": "VIDEO_JOB_ID", "value": video_id}
                            ],
                        }
                    ]
                },
            }
            res = ecs.run_task(**run_params)
            tasks = res.get("tasks", [])
            if tasks:
                task_arn = tasks[0].get("taskArn")
                logger.info(f"ECS task started: {task_arn}")
                return task_arn
        except Exception as e:
            logger.error(f"Failed to launch ECS task: {e}")
        return None


job_queue = JobQueueManager()
