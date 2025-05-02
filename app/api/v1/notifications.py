"""Notification API endpoints."""

from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.admin import Notification
from app.schemas.notification import NotificationResponse
from app.services.notification import NotificationService

router = APIRouter()


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = False,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> List[Notification]:
    """Get user notifications."""
    notification_service = NotificationService(db)
    return await notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset,
    )


@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Dict[str, int]:
    """Get count of unread notifications."""
    notification_service = NotificationService(db)
    count = await notification_service.get_unread_count(user_id=current_user.id)
    return {"count": count}


@router.post("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db),
) -> Dict[str, str]:
    """Mark a notification as read."""
    notification_service = NotificationService(db)
    notification = await notification_service.mark_as_read(notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mark this notification as read",
        )
    return {"message": "Notification marked as read"} 