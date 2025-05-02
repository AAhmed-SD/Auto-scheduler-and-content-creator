"""
S3StorageBackend
---------------
Concrete implementation of StorageBackend for AWS S3.
Handles upload, download, delete, and move operations for S3 buckets.

Security & Compliance:
- Credentials are loaded from environment variables or a secrets manager.
- Never log sensitive information.
- All operations are logged for auditing.
"""
import boto3
from typing import BinaryIO
from .base import StorageBackend, StorageError, logger
import os

class S3StorageBackend(StorageBackend):
    """
    AWS S3 storage backend implementation.
    Uses boto3 for all operations. Credentials and bucket are loaded from environment variables or config.
    """
    def __init__(self, bucket: str, region: str = None):
        self.bucket = bucket
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region,
        )

    def upload(self, file: BinaryIO, path: str) -> str:
        try:
            self.s3.upload_fileobj(file, self.bucket, path)
            url = f"s3://{self.bucket}/{path}"
            logger.info(f"Uploaded file to {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to upload file to S3: {e}")
            raise StorageError("S3 upload failed") from e

    def download(self, path: str) -> bytes:
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=path)
            logger.info(f"Downloaded file from s3://{self.bucket}/{path}")
            return obj["Body"].read()
        except Exception as e:
            logger.error(f"Failed to download file from S3: {e}")
            raise StorageError("S3 download failed") from e

    def delete(self, path: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=path)
            logger.info(f"Deleted file from s3://{self.bucket}/{path}")
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {e}")
            raise StorageError("S3 delete failed") from e

    def move(self, path: str, new_backend: StorageBackend) -> str:
        try:
            data = self.download(path)
            from io import BytesIO
            new_path = new_backend.upload(BytesIO(data), path)
            self.delete(path)
            logger.info(f"Moved file from S3 to {type(new_backend).__name__}: {path}")
            return new_path
        except Exception as e:
            logger.error(f"Failed to move file from S3: {e}")
            raise StorageError("S3 move failed") from e 