"""
FileMetadata Model
-----------------
Tracks files, their storage backend, and metadata for hot/cold automation and auditing.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from enum import Enum as PyEnum

class StorageBackendType(str, PyEnum):
    S3 = "s3"
    B2 = "b2"
    # Add more as needed

class FileMetadata(BaseModel):
    """
    Stores metadata for each file, including storage backend, path, and timestamps.
    Used for tracking, auditing, and hot/cold migration automation.
    """
    __tablename__ = "file_metadata"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, nullable=False, index=True)
    backend = Column(Enum(StorageBackendType), nullable=False)
    url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, index=True)  # Optional: link to user
    # Add more fields as needed (e.g., file size, content type) 