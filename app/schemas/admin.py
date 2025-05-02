"""Admin-related Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.models.admin import AdminLogType


class AdminLogResponse(BaseModel):
    """Response schema for admin logs."""

    id: int
    admin_id: int
    type: AdminLogType
    action: str
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class ContentOverrideRequest(BaseModel):
    """Request schema for content status override."""

    content_id: int = Field(..., description="ID of the content to override")
    new_status: str = Field(..., description="New status to set for the content")
    reason: str = Field(..., description="Reason for the override")


class UserManagementRequest(BaseModel):
    """Request schema for user management actions."""

    user_id: int = Field(..., description="ID of the user to manage")
    action: str = Field(..., description="Action to perform on the user")
    details: Dict[str, Any] = Field(..., description="Additional details for the action") 