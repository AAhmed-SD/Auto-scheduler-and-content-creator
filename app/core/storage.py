"""Storage configuration module."""

import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import magic
from fastapi import UploadFile

from .logging_config import loggers

logger = loggers["root"]


class Storage:
    """Storage class for managing file uploads."""

    def __init__(self):
        """Initialize storage."""
        self.upload_dir = "uploads"
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
        self.allowed_extensions = {
            "image": {"png", "jpg", "jpeg", "gif", "webp"},
            "video": {"mp4", "mov", "avi", "mkv", "webm"},
            "audio": {"mp3", "wav", "ogg", "m4a"},
        }
        self.max_file_size = int(
            os.getenv("MAX_CONTENT_LENGTH", 16777216)
        )  # 16MB default

    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return filename.split(".")[-1].lower()

    def _is_allowed_file(self, file: UploadFile) -> bool:
        """Check if file type is allowed"""
        try:
            # Get file extension
            ext = self._get_file_extension(file.filename)

            # Get file type using python-magic
            file_type = magic.from_buffer(file.file.read(1024), mime=True)
            file.file.seek(0)  # Reset file pointer

            # Check if extension matches file type
            if file_type.startswith("image/"):
                return ext in self.allowed_extensions["image"]
            elif file_type.startswith("video/"):
                return ext in self.allowed_extensions["video"]
            elif file_type.startswith("audio/"):
                return ext in self.allowed_extensions["audio"]

            return False
        except Exception as e:
            logger.error(f"Error checking file type: {str(e)}")
            return False

    async def upload_file(
        self, file: UploadFile, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload a file with optional metadata."""
        try:
            # Create a unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(self.upload_dir, filename)

            # Save the file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            # Return file info
            return {
                "filename": filename,
                "original_name": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "path": file_path,
                "metadata": metadata or {},
            }
        except Exception as e:
            raise RuntimeError(f"Error uploading file: {str(e)}") from e

    def delete_file(self, file_path: str) -> bool:
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted successfully: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False

    def get_file_path(self, project_id: str, filename: str) -> Optional[str]:
        """Get full path of a file"""
        file_path = os.path.join(self.upload_dir, project_id, filename)
        return file_path if os.path.exists(file_path) else None


# Create global storage instance
storage = Storage()
