# backend/app/core/cloud/__init__.py
"""Cloud Provider Integrations for Zero-Cost Scalable Video Generation Architecture.

Includes:
- StorageManager: Unified Local / S3 / Cloudflare R2 object storage
- JobQueueManager: Unified Local / AWS SQS FIFO queue with retry & DLQ
- EventBusManager: Unified WebSocket / AWS SNS event publishing
"""

from .storage import storage_manager
from .queue import job_queue
from .events import event_bus

__all__ = ["storage_manager", "job_queue", "event_bus"]
