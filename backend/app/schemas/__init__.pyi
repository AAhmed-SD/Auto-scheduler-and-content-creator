from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str
    exp: datetime

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = False
    settings: Dict[str, Any] = {}

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    allowed_users: List[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ContentBase(BaseModel):
    title: str
    content_type: str
    description: Optional[str] = None
    media_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    status: str

class ContentCreate(ContentBase):
    project_id: int

class ContentUpdate(ContentBase):
    pass

class ContentResponse(ContentBase):
    id: int
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ScheduleBase(BaseModel):
    content_id: int
    schedule_time: datetime
    repeat: bool = False
    repeat_interval: Optional[str] = None
    status: str = "pending"

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    pass

class ScheduleResponse(ScheduleBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True 