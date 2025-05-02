"""Notification service for sending and managing notifications."""

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.admin import Notification, NotificationStatus, NotificationType
from app.models.user import User
from app.services.email import send_email
from app.services.push import send_push_notification


class NotificationService:
    """Service for handling notifications."""

    def __init__(self, db: Session):
        self.db = db

    async def create_notification(
        self,
        user: User,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            user_id=user.id,
            type=notification_type,
            title=title,
            message=message,
            data=json.dumps(data) if data else None,
        )
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    async def send_notification(
        self,
        notification: Notification,
        request: Optional[Request] = None,
    ) -> None:
        """Send a notification through appropriate channels."""
        try:
            # Send email notification
            if notification.user.email_notifications:
                await send_email(
                    to_email=notification.user.email,
                    subject=notification.title,
                    body=notification.message,
                )

            # Send push notification
            if notification.user.push_notifications:
                await send_push_notification(
                    user_id=notification.user.id,
                    title=notification.title,
                    message=notification.message,
                    data=json.loads(notification.data) if notification.data else None,
                )

            # Update notification status
            notification.status = NotificationStatus.SENT
            self.db.commit()

        except Exception as e:
            notification.status = NotificationStatus.FAILED
            self.db.commit()
            raise e

    async def mark_as_read(self, notification_id: int) -> Notification:
        """Mark a notification as read."""
        notification = self.db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.read_at = datetime.utcnow()
            self.db.commit()
        return notification

    async def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Notification]:
        """Get notifications for a user."""
        query = self.db.query(Notification).filter(Notification.user_id == user_id)
        if unread_only:
            query = query.filter(Notification.read_at.is_(None))
        return query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()

    async def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        return (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.read_at.is_(None),
            )
            .count()
        ) 