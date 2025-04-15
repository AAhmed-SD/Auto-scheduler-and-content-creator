import os
from fastapi import UploadFile
from typing import Optional, Dict, Any
import magic
from datetime import datetime
import shutil
from pathlib import Path
import logging
from .logging_config import loggers

logger = loggers['root']

class ContentStorage:
    def __init__(self):
        self.upload_dir = os.getenv('UPLOAD_FOLDER', 'uploads')
        self.allowed_extensions = {
            'image': {'png', 'jpg', 'jpeg', 'gif', 'webp'},
            'video': {'mp4', 'mov', 'avi', 'mkv', 'webm'},
            'audio': {'mp3', 'wav', 'ogg', 'm4a'}
        }
        self.max_file_size = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB default
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        """Ensure upload directory exists"""
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)

    def _get_file_extension(self, filename: str) -> str:
        """Get file extension from filename"""
        return filename.split('.')[-1].lower()

    def _is_allowed_file(self, file: UploadFile) -> bool:
        """Check if file type is allowed"""
        try:
            # Get file extension
            ext = self._get_file_extension(file.filename)
            
            # Get file type using python-magic
            file_type = magic.from_buffer(file.file.read(1024), mime=True)
            file.file.seek(0)  # Reset file pointer
            
            # Check if extension matches file type
            if file_type.startswith('image/'):
                return ext in self.allowed_extensions['image']
            elif file_type.startswith('video/'):
                return ext in self.allowed_extensions['video']
            elif file_type.startswith('audio/'):
                return ext in self.allowed_extensions['audio']
            
            return False
        except Exception as e:
            logger.error(f"Error checking file type: {str(e)}")
            return False

    async def save_file(self, file: UploadFile, project_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Save uploaded file with metadata"""
        try:
            # Validate file
            if not self._is_allowed_file(file):
                raise ValueError("File type not allowed")

            # Create project directory
            project_dir = os.path.join(self.upload_dir, project_id)
            Path(project_dir).mkdir(parents=True, exist_ok=True)

            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(project_dir, filename)

            # Save file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Prepare metadata
            file_metadata = {
                'filename': filename,
                'original_name': file.filename,
                'content_type': file.content_type,
                'size': os.path.getsize(file_path),
                'path': file_path,
                'project_id': project_id,
                'created_at': datetime.now().isoformat(),
                **(metadata or {})
            }

            logger.info(f"File saved successfully: {filename}")
            return file_metadata

        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise

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
storage = ContentStorage() 