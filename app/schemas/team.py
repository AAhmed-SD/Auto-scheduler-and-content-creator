from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class TeamCreate(TeamBase):
    pass


class TeamResponse(TeamBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    team_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberAdd(BaseModel):
    user_id: int


class ProjectMemberAdd(BaseModel):
    user_id: int
    role: str = Field(..., min_length=1, max_length=50)
    permissions: Optional[Dict[str, bool]] = Field(
        default_factory=lambda: {
            "create_content": True,
            "edit_content": True,
            "delete_content": False,
            "schedule_posts": True,
            "view_analytics": True,
            "manage_members": False,
        }
    )


class RoleUpdate(BaseModel):
    role: str = Field(..., min_length=1, max_length=50)
    permissions: Dict[str, bool]


class TeamMemberResponse(BaseModel):
    user_id: int
    username: str
    role: str
    permissions: Optional[Dict[str, bool]]

    class Config:
        from_attributes = True


class ProjectMemberResponse(TeamMemberResponse):
    project_role: Optional[str]
    project_permissions: Optional[Dict[str, bool]]


class TeamWithMembers(TeamResponse):
    members: List[TeamMemberResponse]


class ProjectWithMembers(ProjectResponse):
    members: List[ProjectMemberResponse]
