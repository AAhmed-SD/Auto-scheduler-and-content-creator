from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum, Text, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from typing import Dict, Any, List, Optional
from .base import BaseModel
import uuid
from enum import Enum as PyEnum


class ContentType(str, PyEnum):
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"


class ContentStatus(str, PyEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class Content(BaseModel):
    __tablename__ = "content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    media_urls = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    style_template: Column[Optional[Dict[str, Any]]] = Column(JSON)
    media_url = Column(String)
    thumbnail_url = Column(String)
    platform_specific_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    file_path = Column(String, nullable=True)

    # Relationships
    project = relationship("Project", back_populates="content")
    creator = relationship("User", back_populates="content")
    categories = relationship("Category", secondary="content_categories", back_populates="content")
    tags = relationship("Tag", secondary="content_tags", back_populates="content")
    social_media_posts = relationship("SocialMediaPost", back_populates="content")
    approvals = relationship("ContentApproval", back_populates="content")
    performance_metrics = relationship("ContentPerformance", back_populates="content")
    schedules = relationship("Schedule", back_populates="content")
    analytics = relationship("Analytics", back_populates="content")

    def __repr__(self):
        return f"<Content {self.title}>"


class Schedule(BaseModel):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"))
    platform = Column(String, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")
    captions: Column[Optional[Dict[str, str]]] = Column(JSON)
    hashtags: Column[Optional[List[str]]] = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    content = relationship("Content", back_populates="schedules")
