from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from typing import Dict, Any, List, Optional
from .base import BaseModel


class ContentType(str, enum.Enum):
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"
    CAROUSEL = "carousel"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class Content(BaseModel):
    __tablename__ = "content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(Enum(ContentType), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    style_template: Column[Optional[Dict[str, Any]]] = Column(JSON)
    media_url = Column(String)
    thumbnail_url = Column(String)
    metadata = Column(JSON, nullable=True)
    platform_specific_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    file_path = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="content")
    schedules = relationship("Schedule", back_populates="content")
    analytics = relationship("Analytics", back_populates="content")

    def __repr__(self):
        return f"<Content {self.title} ({self.type})>"


class Schedule(BaseModel):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.id"))
    platform = Column(String, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")
    captions: Column[Optional[Dict[str, str]]] = Column(JSON)
    hashtags: Column[Optional[List[str]]] = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    content = relationship("Content", back_populates="schedules")
