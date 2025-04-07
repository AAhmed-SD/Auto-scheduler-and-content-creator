from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class User(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    created_at: datetime
    updated_at: datetime


class Content(BaseModel):
    id: str
    user_id: str
    type: str  # "text", "image", "video"
    content: str
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class Schedule(BaseModel):
    id: str
    user_id: str
    content_id: str
    platforms: List[str]
    schedule_time: datetime
    repeat: bool
    repeat_interval: Optional[str]  # "daily", "weekly", "monthly"
    status: str  # "scheduled", "completed", "failed"
    created_at: datetime
    updated_at: datetime


class Media(BaseModel):
    id: str
    user_id: str
    type: str  # "image", "video"
    url: str
    size: int
    metadata: Optional[dict] = None
    created_at: datetime
    updated_at: datetime


class Platform(BaseModel):
    id: str
    name: str
    type: str  # "social", "email", "blog"
    credentials: dict
    created_at: datetime
    updated_at: datetime


class Analytics(BaseModel):
    id: str
    user_id: str
    content_id: str
    platform: str
    metrics: dict
    created_at: datetime
    updated_at: datetime
