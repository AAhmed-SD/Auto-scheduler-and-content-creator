"""Team routes for the application."""

from typing import Dict, List, Optional, Sequence, Any
from sqlalchemy import and_, select, update

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..core.database import get_db
from ..models.project import Project
from ..models.team import Team
from ..models.user import User
from ..models.user_role import UserRole
from ..schemas.team import (
    ProjectCreate,
    ProjectMemberAdd,
    ProjectResponse,
    RoleUpdate,
    TeamCreate,
    TeamMemberAdd,
    TeamMemberResponse,
    TeamResponse,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("", response_model=TeamResponse)
async def create_team(team: TeamCreate, db: Session = Depends(get_db)) -> TeamResponse:
    """Create a new team"""
    try:
        db_team = Team(**team.dict())
        db.add(db_team)
        db.commit()
        db.refresh(db_team)
        return TeamResponse.from_orm(db_team)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/projects", response_model=ProjectResponse)
async def create_project(
    team_id: int,
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """Create a new project in a team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if current_user not in team.members:
        raise HTTPException(status_code=403, detail="Not a team member")

    db_project = Project(
        name=project.name,
        description=project.description,
        team_id=team_id
    )
    db_project.members.append(current_user)  # Add creator as member
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return ProjectResponse.from_orm(db_project)


@router.post("/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: int,
    member: TeamMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> TeamMemberResponse:
    """Add a member to a team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if current_user not in team.members:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_member = db.query(User).filter(User.id == member.user_id).first()
    if not new_member:
        raise HTTPException(status_code=404, detail="User not found")

    team.members.append(new_member)
    db.commit()
    return TeamMemberResponse.from_orm(new_member)


@router.post("/projects/{project_id}/members", response_model=Dict[str, str])
async def add_project_member(
    project_id: int,
    member: ProjectMemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Add a member to a project with role"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user not in project.team.members:
        raise HTTPException(status_code=403, detail="Not authorized")

    new_member = db.query(User).filter(User.id == member.user_id).first()
    if not new_member:
        raise HTTPException(status_code=404, detail="User not found")

    # Add member with role
    role = UserRole(
        user_id=new_member.id,
        project_id=project_id,
        role=member.role,
        permissions=member.permissions
    )
    db.add(role)
    project.members.append(new_member)
    db.commit()
    return {"status": "success"}


@router.get("/teams/{team_id}/projects", response_model=List[ProjectResponse])
async def get_team_projects(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Sequence[ProjectResponse]:
    """Get all projects for a team"""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team or current_user not in team.members:
        raise HTTPException(status_code=403, detail="Not authorized")

    return [ProjectResponse.from_orm(project) for project in team.projects]


@router.get("/projects/{project_id}/members", response_model=List[Dict[str, Any]])
async def get_project_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get all members of a project with their roles"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project or current_user not in project.members:
        raise HTTPException(status_code=403, detail="Not authorized")

    members = []
    for member in project.members:
        role = (
            db.query(UserRole)
            .filter(UserRole.user_id == member.id, UserRole.project_id == project_id)
            .first()
        )
        members.append({
            "user_id": member.id,
            "username": member.username,
            "role": role.role if role else "member",
            "permissions": role.permissions if role else None
        })
    return members


@router.put("/projects/{project_id}/members/{user_id}/role")
async def update_project_role(
    project_id: int,
    user_id: int,
    role_update: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    # Verify project exists and user has permission
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Check if current user has permission to update roles
    user_role = db.query(UserRole).filter(
        and_(
            UserRole.project_id == project_id,
            UserRole.user_id == current_user.id
        )
    ).first()
    
    if not user_role or bool(user_role.role != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to update roles")

    # Update the user's role
    target_role = db.query(UserRole).filter(
        and_(
            UserRole.project_id == project_id,
            UserRole.user_id == user_id
        )
    ).first()
    
    if not target_role:
        raise HTTPException(status_code=404, detail="User not found in project")

    # Update role and permissions
    target_role.role = role_update.get("role", target_role.role)
    target_role.permissions = role_update.get("permissions", target_role.permissions)
    db.commit()
    
    return {"message": "Role updated successfully"}
