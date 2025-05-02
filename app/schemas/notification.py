"""Notification-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from app.models.admin import NotificationType, NotificationStatus


class NotificationResponse(BaseModel):
    """Response schema for notifications."""

    id: int
    user_id: int
    type: NotificationType
    status: NotificationStatus
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 