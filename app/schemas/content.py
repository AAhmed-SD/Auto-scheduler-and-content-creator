"""Content schemas for the application."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel

class ContentStatus(str, Enum):
    """Content status enumeration."""
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class ContentBase(BaseModel):
    """Base content schema."""
    title: str
    description: Optional[str] = None
    content_type: str
    status: ContentStatus = ContentStatus.DRAFT

class ContentCreate(ContentBase):
    """Schema for creating content."""
    project_id: int

class ContentUpdate(ContentBase):
    """Schema for updating content."""
    pass

class ContentResponse(ContentBase):
    """Schema for content response."""
    id: int
    creator_id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        """Pydantic config."""
        orm_mode = True 