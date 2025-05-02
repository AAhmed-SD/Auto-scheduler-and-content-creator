"""Client approval schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from ..models.collaboration import ApprovalStatus


class ClientApprovalBase(BaseModel):
    """Base schema for client approvals."""
    content_id: int
    client_id: int
    is_urgent: bool = False
    deadline_days: int = Field(default=7, ge=1, le=30)


class ClientApprovalCreate(ClientApprovalBase):
    """Schema for creating client approvals."""
    pass


class ClientApprovalUpdate(BaseModel):
    """Schema for updating client approvals."""
    status: Optional[ApprovalStatus] = None
    feedback: Optional[str] = None
    requested_changes: Optional[str] = None


class ClientApprovalResponse(ClientApprovalBase):
    """Schema for client approval responses."""
    id: int
    agency_id: int
    status: ApprovalStatus
    feedback: Optional[str] = None
    requested_changes: Optional[str] = None
    deadline: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 