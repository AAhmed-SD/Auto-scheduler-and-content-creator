"""
B2StorageBackend
---------------
Concrete implementation of StorageBackend for Backblaze B2.
Handles upload, download, delete, and move operations for B2 buckets.

Security & Compliance:
- Credentials are loaded from environment variables or a secrets manager.
- Never log sensitive information.
- All operations are logged for auditing.
"""
from typing import BinaryIO
from .base import StorageBackend, StorageError, logger
import os
import b2sdk.v2 as b2

class B2StorageBackend(StorageBackend):
    """
    Backblaze B2 storage backend implementation.
    Uses b2sdk for all operations. Credentials and bucket are loaded from environment variables or config.
    """
    def __init__(self, bucket: str):
        self.bucket_name = bucket
        self.account_id = os.getenv("B2_ACCOUNT_ID")
        self.application_key = os.getenv("B2_APPLICATION_KEY")
        self.b2_api = b2.B2Api()
        self.b2_api.authorize_account("production", self.account_id, self.application_key)
        self.bucket = self.b2_api.get_bucket_by_name(self.bucket_name)

    def upload(self, file: BinaryIO, path: str) -> str:
        try:
            self.bucket.upload_bytes(file.read(), path)
            url = f"b2://{self.bucket_name}/{path}"
            logger.info(f"Uploaded file to {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to upload file to B2: {e}")
            raise StorageError("B2 upload failed") from e

    def download(self, path: str) -> bytes:
        try:
            file_version = self.bucket.download_file_by_name(path)
            logger.info(f"Downloaded file from b2://{self.bucket_name}/{path}")
            return file_version.read()
        except Exception as e:
            logger.error(f"Failed to download file from B2: {e}")
            raise StorageError("B2 download failed") from e

    def delete(self, path: str) -> None:
        try:
            file_version = self.bucket.get_file_info_by_name(path)
            self.bucket.delete_file_version(file_version.id_, path)
            logger.info(f"Deleted file from b2://{self.bucket_name}/{path}")
        except Exception as e:
            logger.error(f"Failed to delete file from B2: {e}")
            raise StorageError("B2 delete failed") from e

    def move(self, path: str, new_backend: StorageBackend) -> str:
        try:
            data = self.download(path)
            from io import BytesIO
            new_path = new_backend.upload(BytesIO(data), path)
            self.delete(path)
            logger.info(f"Moved file from B2 to {type(new_backend).__name__}: {path}")
            return new_path
        except Exception as e:
            logger.error(f"Failed to move file from B2: {e}")
            raise StorageError("B2 move failed") from e 