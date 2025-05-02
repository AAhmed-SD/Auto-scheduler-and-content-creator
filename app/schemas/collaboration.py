from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .team import UserResponse


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    user_id: int
    content_item_id: int
    created_at: datetime
    updated_at: datetime
    user: UserResponse
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


class ApprovalBase(BaseModel):
    status: str = Field(..., pattern="^(pending|approved|rejected)$")
    feedback: Optional[str] = Field(None, max_length=500)


class ApprovalCreate(ApprovalBase):
    pass


class ApprovalResponse(ApprovalBase):
    id: int
    content_item_id: int
    approver_id: int
    created_at: datetime
    updated_at: datetime
    approver: UserResponse

    class Config:
        from_attributes = True


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    assignee_id: int
    due_date: Optional[datetime]


class TaskCreate(TaskBase):
    pass


class TaskResponse(TaskBase):
    id: int
    content_item_id: int
    creator_id: int
    status: str
    created_at: datetime
    updated_at: datetime
    assignee: UserResponse
    creator: UserResponse

    class Config:
        from_attributes = True


class ClientShareBase(BaseModel):
    expires_in_days: int = Field(default=7, ge=1, le=30)


class ClientShareCreate(ClientShareBase):
    pass


class ClientShareResponse(BaseModel):
    id: int
    project_id: int
    share_token: str
    expires_at: datetime
    is_active: bool
    created_at: datetime
    created_by_id: int

    class Config:
        from_attributes = True


class ContentVersionBase(BaseModel):
    content_data: Dict


class ContentVersionCreate(ContentVersionBase):
    pass


class ContentVersionResponse(ContentVersionBase):
    id: int
    content_item_id: int
    version_number: int
    created_by_id: int
    created_at: datetime
    status: str
    created_by: UserResponse

    class Config:
        from_attributes = True


# For handling mentions in comments
class MentionCreate(BaseModel):
    user_id: int


class MentionResponse(BaseModel):
    id: int
    comment_id: int
    user_id: int
    user: UserResponse

    class Config:
        from_attributes = True


# For task status updates
class TaskStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(todo|in_progress|blocked|completed)$")
    comment: Optional[str] = Field(None, max_length=500)


# For content workflow
class WorkflowTransition(BaseModel):
    from_status: str
    to_status: str
    comment: Optional[str] = Field(None, max_length=500)
    notify_users: List[int] = []  # List of user IDs to notify
