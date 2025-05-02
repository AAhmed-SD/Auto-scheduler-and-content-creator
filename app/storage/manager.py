"""
StorageManager
--------------
Central manager for all file operations. Selects the backend based on config or function argument.
"""
from typing import BinaryIO, Optional
from .base import StorageBackend
from .s3 import S3StorageBackend
from .b2 import B2StorageBackend
import os

class StorageManager:
    """
    StorageManager routes file operations to the correct backend.
    - Uses config (DEFAULT_STORAGE_BACKEND) or per-operation override.
    - Supports easy registration of new backends.
    """
    def __init__(self):
        self.backends = {
            "s3": S3StorageBackend(
                bucket=os.getenv("S3_BUCKET", "my-s3-bucket"),
                region=os.getenv("AWS_REGION", "us-east-1")
            ),
            "b2": B2StorageBackend(
                bucket=os.getenv("B2_BUCKET", "my-b2-bucket")
            ),
        }
        self.default_backend = os.getenv("DEFAULT_STORAGE_BACKEND", "s3")

    def get_backend(self, backend: Optional[str] = None) -> StorageBackend:
        key = backend or self.default_backend
        if key not in self.backends:
            raise ValueError(f"Unknown storage backend: {key}")
        return self.backends[key]

    def upload(self, file: BinaryIO, path: str, backend: Optional[str] = None) -> str:
        return self.get_backend(backend).upload(file, path)

    def download(self, path: str, backend: Optional[str] = None) -> bytes:
        return self.get_backend(backend).download(path)

    def delete(self, path: str, backend: Optional[str] = None) -> None:
        self.get_backend(backend).delete(path)

    def move(self, path: str, from_backend: Optional[str], to_backend: str) -> str:
        src = self.get_backend(from_backend)
        dst = self.get_backend(to_backend)
        return src.move(path, dst)

    def register_backend(self, name: str, backend: StorageBackend):
        """
        Register a new backend at runtime.
        """
        self.backends[name] = backend 