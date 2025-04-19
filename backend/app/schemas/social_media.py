from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
from enum import Enum

class Platform(str, Enum):
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    TWITTER = "twitter"

class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    TEXT = "text"

class PostStatus(str, Enum):
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"

class User(BaseModel):
    id: str
    username: str
    platform: Platform
    followers: int = Field(ge=0)
    following: int = Field(ge=0)
    profile_picture: HttpUrl

class ContentStructure(BaseModel):
    caption: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    media_type: MediaType

class Template(BaseModel):
    id: str
    name: str
    platform: Platform
    structure: ContentStructure

class PostContent(BaseModel):
    text: str
    media_url: Optional[HttpUrl] = None
    media_type: MediaType
    hashtags: List[str] = Field(default_factory=list)

class PostMetrics(BaseModel):
    likes: int = Field(ge=0)
    comments: int = Field(ge=0)
    shares: int = Field(ge=0)
    reach: int = Field(ge=0)

class Post(BaseModel):
    id: Optional[str] = None  # Optional for creation
    platform: Platform
    content: PostContent
    scheduled_time: datetime
    status: Optional[PostStatus] = PostStatus.SCHEDULED
    metrics: Optional[PostMetrics] = None

class PostCreate(BaseModel):
    platform: Platform
    content: PostContent
    scheduled_time: datetime

class PostUpdate(PostCreate):
    pass

class AnalyticsMetrics(BaseModel):
    followers: int = Field(ge=0)
    engagement_rate: float = Field(ge=0, le=100)
    reach: int = Field(ge=0)
    impressions: int = Field(ge=0)

class Analytics(BaseModel):
    date: datetime
    metrics: AnalyticsMetrics

# Response Models
class UserResponse(User):
    pass

class TemplateResponse(Template):
    pass

class PostResponse(Post):
    pass

class AnalyticsResponse(Analytics):
    pass

class MessageResponse(BaseModel):
    message: str 