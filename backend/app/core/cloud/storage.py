# backend/app/core/cloud/storage.py
"""Unified Storage Manager supporting Local Filesystem, AWS S3, and Cloudflare R2.

Cloudflare R2 provides 10GB permanent free storage with ZERO egress bandwidth fees,
making it the ideal choice for $0-cost video distribution.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import Optional
from app.core.config import settings

logger = logging.getLogger("app.cloud.storage")


class StorageManager:
    """Manages video and asset file storage across local and cloud providers."""

    def __init__(self):
        self.backend = settings.STORAGE_BACKEND.lower()
        self.bucket_name = settings.S3_BUCKET_NAME
        self.endpoint_url = settings.S3_ENDPOINT_URL
        self.region = settings.AWS_REGION
        self.static_dir = Path(__file__).parent.parent.parent / "static"
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self._s3_client = None

    def _get_s3_client(self):
        """Lazy initialization of boto3 S3 client."""
        if self._s3_client is None:
            try:
                import boto3
                from botocore.config import Config

                config = Config(
                    signature_version="s3v4",
                    retries={"max_attempts": 3, "mode": "standard"},
                )
                self._s3_client = boto3.client(
                    "s3",
                    endpoint_url=self.endpoint_url,
                    region_name=self.region,
                    config=config,
                )
            except ImportError:
                logger.warning(
                    "boto3 not installed. Falling back to local storage backend."
                )
                self.backend = "local"
        return self._s3_client

    async def upload_video(
        self, local_file_path: str, destination_name: Optional[str] = None
    ) -> str:
        """Uploads a generated video file and returns its public or streaming URL.

        Args:
            local_file_path: Local path to the rendered .mp4 file
            destination_name: Key or filename in storage (default: basename)

        Returns:
            URL string accessible by the client/frontend
        """
        source = Path(local_file_path)
        if not source.exists():
            raise FileNotFoundError(f"Source video not found at: {local_file_path}")

        key = destination_name or source.name

        if self.backend in ("s3", "r2") and self.bucket_name:
            client = self._get_s3_client()
            if client:
                try:
                    logger.info(f"Uploading {key} to {self.backend.upper()} bucket {self.bucket_name}")
                    client.upload_file(
                        Filename=str(source),
                        Bucket=self.bucket_name,
                        Key=key,
                        ExtraArgs={"ContentType": "video/mp4"},
                    )

                    # Return public CDN URL or pre-signed URL
                    if self.endpoint_url:
                        # R2 Custom Domain or S3 endpoint
                        return f"{self.endpoint_url}/{self.bucket_name}/{key}"
                    return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
                except Exception as e:
                    logger.error(f"Cloud upload failed ({e}), falling back to local static serving")

        # Local storage fallback
        dest = self.static_dir / key
        if source.resolve() != dest.resolve():
            shutil.copy2(source, dest)
        return f"/static/{key}"

    async def delete_video(self, filename: str) -> bool:
        """Deletes a video file from local or cloud storage."""
        if self.backend in ("s3", "r2") and self.bucket_name:
            client = self._get_s3_client()
            if client:
                try:
                    client.delete_object(Bucket=self.bucket_name, Key=filename)
                    return True
                except Exception as e:
                    logger.error(f"Failed to delete {filename} from S3/R2: {e}")

        local_file = self.static_dir / filename
        if local_file.exists():
            local_file.unlink()
            return True
        return False


storage_manager = StorageManager()
