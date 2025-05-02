"""Admin and notification models."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import BaseModel


class NotificationType(str, Enum):
    CONTENT_APPROVED = "content_approved"
    CONTENT_REJECTED = "content_rejected"
    CONTENT_LIVE = "content_live"
    ERROR = "error"
    SYSTEM = "system"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"


class Notification(BaseModel):
    """Notification model for user notifications."""

    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(SQLEnum(NotificationType), nullable=False)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(Text)  # JSON string of additional data
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="notifications")


class AdminLogType(str, Enum):
    USER_MANAGEMENT = "user_management"
    CONTENT_OVERRIDE = "content_override"
    SYSTEM_OVERRIDE = "system_override"
    BUG_FIX = "bug_fix"
    TASK_MANAGEMENT = "task_management"
    SETTINGS_CHANGE = "settings_change"


class AdminLog(BaseModel):
    """Admin log model for tracking admin actions."""

    __tablename__ = "admin_logs"

    admin_id = Column(Integer, ForeignKey("users.id"))
    type = Column(SQLEnum(AdminLogType), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(Text)  # JSON string of action details
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    admin = relationship("User", back_populates="admin_logs") 