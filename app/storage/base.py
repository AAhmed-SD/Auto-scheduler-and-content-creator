"""
StorageBackend Interface
-----------------------
Defines the interface for all storage backends (S3, B2, etc.).
All storage backends must implement this interface.

Security & Compliance:
- All credentials must be loaded from environment variables or a secrets manager.
- Never log sensitive information (e.g., credentials, tokens).
- All file operations should be auditable and logged.
"""
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
import logging

logger = logging.getLogger("storage")

class StorageError(Exception):
    """Custom exception for storage-related errors."""
    pass

class StorageBackend(ABC):
    """
    Abstract base class for storage backends.
    All storage backends (S3, B2, local, etc.) must implement these methods.
    Security:
    - Use environment variables for credentials.
    - Log all operations and errors (never log secrets).
    - Raise StorageError for all backend-specific errors.
    """

    @abstractmethod
    def upload(self, file: BinaryIO, path: str) -> str:
        """
        Upload a file to the storage backend.
        Args:
            file: File-like object to upload.
            path: Destination path in the storage backend.
        Returns:
            The URL or identifier of the uploaded file.
        Raises:
            StorageError: If upload fails.
        """
        pass

    @abstractmethod
    def download(self, path: str) -> bytes:
        """
        Download a file from the storage backend.
        Args:
            path: Path or identifier of the file in the storage backend.
        Returns:
            The file content as bytes.
        Raises:
            StorageError: If download fails.
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """
        Delete a file from the storage backend.
        Args:
            path: Path or identifier of the file in the storage backend.
        Raises:
            StorageError: If delete fails.
        """
        pass

    @abstractmethod
    def move(self, path: str, new_backend: 'StorageBackend') -> str:
        """
        Move a file from this backend to another backend.
        Args:
            path: Path or identifier of the file in this backend.
            new_backend: The target storage backend instance.
        Returns:
            The new path or identifier in the target backend.
        Raises:
            StorageError: If move fails.
        """
        pass 