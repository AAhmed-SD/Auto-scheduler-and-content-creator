from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from sqlalchemy import Column
from sqlalchemy.orm import relationship

class User:
    id: Column[int]
    email: Column[str]
    hashed_password: Column[str]
    full_name: Column[Optional[str]]
    is_active: Column[bool]
    created_at: Column[datetime]
    updated_at: Column[datetime]

class Project:
    id: Column[int]
    name: Column[str]
    description: Column[Optional[str]]
    owner_id: Column[int]
    is_private: Column[bool]
    settings: Column[Dict[str, Any]]
    allowed_users: Column[List[int]]
    created_at: Column[datetime]
    updated_at: Column[datetime]
    owner: relationship
    contents: relationship

class Content:
    id: Column[int]
    title: Column[str]
    content_type: Column[str]
    description: Column[Optional[str]]
    media_url: Column[Optional[str]]
    metadata: Column[Dict[str, Any]]
    status: Column[str]
    project_id: Column[int]
    user_id: Column[int]
    created_at: Column[datetime]
    updated_at: Column[datetime]
    project: relationship
    user: relationship

class Schedule:
    id: Column[int]
    content_id: Column[int]
    user_id: Column[int]
    schedule_time: Column[datetime]
    repeat: Column[bool]
    repeat_interval: Column[Optional[str]]
    status: Column[str]
    created_at: Column[datetime]
    updated_at: Column[datetime]
    content: relationship
    user: relationship 