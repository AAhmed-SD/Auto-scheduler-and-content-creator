from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Enum, Text, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from typing import Dict, Any, List, Optional
from .base import Base
import uuid
from enum import Enum as PyEnum
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ContentType(str, PyEnum):
    VIDEO = "video"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"
    CAROUSEL = "carousel"
    STORY = "story"
    REEL = "reel"
    LINK = "link"


class ContentStatus(str, PyEnum):
    DRAFT = "draft"
    GENERATING = "generating"
    READY = "ready"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    ARCHIVED = "archived"


class Content(Base):
    __tablename__ = "content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text)
    content_type = Column(Enum(ContentType), nullable=False)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    media_urls = Column(JSON, default=[])
    content_metadata = Column(JSON, default={})
    style_template = Column(JSON)
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


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(UUID(as_uuid=True), ForeignKey("content.id"))
    platform = Column(String, nullable=False)
    scheduled_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")
    captions = Column(JSON)
    hashtags = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    content = relationship("Content", back_populates="schedules")


class ContentTemplate(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content_type: ContentType
    template: str = Field(..., min_length=1)
    variables: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('variables')
    def validate_variables(cls, v, values):
        if 'template' in values:
            template = values['template']
            for var in v:
                if f"{{{var}}}" not in template:
                    raise ValueError(f"Variable {var} not found in template")
        return v

    @validator('template')
    def validate_template(cls, v, values):
        if 'content_type' in values:
            content_type = values['content_type']
            if content_type == ContentType.TEXT and len(v) > 280:
                raise ValueError("Text content cannot exceed 280 characters")
        return v


class ContentTemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content_type: ContentType
    template: str = Field(..., min_length=1)
    variables: List[str] = Field(default_factory=list)


class ContentTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    content_type: Optional[ContentType] = None
    template: Optional[str] = Field(None, min_length=1)
    variables: Optional[List[str]] = None
