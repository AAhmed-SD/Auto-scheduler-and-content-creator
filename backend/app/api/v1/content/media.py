from typing import Optional, Dict, Any, cast
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from app.core.security import get_current_user
from app.models.user import User
from app.services.media_service import MediaService
from sqlalchemy.orm import Session
from app.core.database import get_db
import os
from pathlib import Path

router = APIRouter()


@router.post("/upload")
async def upload_media(
    file: UploadFile = File(...),
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Upload media file."""
    media_service = MediaService(db)

    # Validate file type
    filename = cast(str, file.filename)
    file_extension = Path(filename).suffix.lower()
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov"}
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}",
        )

    # Upload file
    media_url = await media_service.upload_file(
        file, filename, project_id, current_user.id
    )

    return {"media_url": media_url}


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """Delete media file."""
    media_service = MediaService(db)
    await media_service.delete_file(media_id, current_user.id)
    return {"message": "Media deleted successfully"}
