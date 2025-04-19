from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .social_media import Platform, Template

class ProjectStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class ContentGenerationType(str, Enum):
    TEMPLATE_BASED = "template_based"
    AI_GENERATED = "ai_generated"

class InspirationMedia(BaseModel):
    url: HttpUrl
    media_type: str  # "image" or "video"
    description: Optional[str] = None

class ContentPrompt(BaseModel):
    text: str
    tone: Optional[str] = None
    target_audience: Optional[str] = None
    key_points: Optional[List[str]] = None
    inspiration_media: Optional[List[InspirationMedia]] = None

class Project(BaseModel):
    id: Optional[str] = None
    user_id: str
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    platform: Platform
    generation_type: ContentGenerationType
    template_id: Optional[str] = None  # If using template
    content_prompt: Optional[ContentPrompt] = None  # If using AI generation
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime
    updated_at: datetime

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    platform: Platform
    generation_type: ContentGenerationType
    template_id: Optional[str] = None
    content_prompt: Optional[ContentPrompt] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    platform: Optional[Platform] = None
    generation_type: Optional[ContentGenerationType] = None
    template_id: Optional[str] = None
    content_prompt: Optional[ContentPrompt] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(Project):
    pass

class DashboardStats(BaseModel):
    total_projects: int
    projects_by_status: dict[ProjectStatus, int]
    projects_by_platform: dict[Platform, int]
    recent_projects: List[ProjectResponse] 