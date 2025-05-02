"""
Hot/Cold Storage Policy & Automation
-----------------------------------
Defines policy for hot/cold storage and a Celery task to migrate files automatically.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.file import FileMetadata, StorageBackendType
from app.storage.manager import StorageManager
import os

# Policy: files older than this (in days) are considered cold
HOT_STORAGE_MAX_AGE_DAYS = int(os.getenv("HOT_STORAGE_MAX_AGE_DAYS", 30))
COLD_BACKEND = StorageBackendType.B2
HOT_BACKEND = StorageBackendType.S3

# Celery task (pseudo-code, integrate with your Celery app)
def migrate_hot_to_cold(db: Session):
    """
    Finds files in hot storage older than policy and migrates them to cold storage.
    Updates metadata in the database.
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(days=HOT_STORAGE_MAX_AGE_DAYS)
    storage = StorageManager()
    files = db.query(FileMetadata).filter(
        FileMetadata.backend == HOT_BACKEND,
        FileMetadata.uploaded_at < cutoff
    ).all()
    for file in files:
        # Move file to cold backend
        new_url = storage.move(file.path, from_backend=HOT_BACKEND, to_backend=COLD_BACKEND)
        file.backend = COLD_BACKEND
        file.url = new_url
        file.last_accessed_at = now
        db.add(file)
    db.commit()

"""
Summary:
- Policy is config-driven (HOT_STORAGE_MAX_AGE_DAYS).
- Celery task migrates files from S3 to B2 if they are older than the policy.
- Metadata is updated for auditing and future queries.
""" 