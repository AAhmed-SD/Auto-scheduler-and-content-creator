from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.services.project_service import ProjectService
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: bool = True
    settings: Optional[dict] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    settings: Optional[dict] = None


@router.post("/", response_model=ProjectCreate)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new project."""
    project_service = ProjectService(db)
    return project_service.create_project(
        name=project.name,
        owner_id=current_user.id,
        description=project.description,
        is_private=project.is_private,
        settings=project.settings,
    )


@router.get("/", response_model=List[ProjectCreate])
async def get_projects(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all projects accessible to the current user."""
    project_service = ProjectService(db)
    return project_service.get_user_projects(current_user.id)


@router.get("/{project_id}", response_model=ProjectCreate)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific project."""
    project_service = ProjectService(db)
    return project_service.get_project(project_id, current_user.id)


@router.put("/{project_id}", response_model=ProjectCreate)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a project."""
    project_service = ProjectService(db)
    return project_service.update_project(
        project_id=project_id,
        user_id=current_user.id,
        name=project.name,
        description=project.description,
        is_private=project.is_private,
        settings=project.settings,
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a project."""
    project_service = ProjectService(db)
    return project_service.delete_project(project_id, current_user.id)


@router.post("/{project_id}/members/{user_id}")
async def add_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a user to a project."""
    project_service = ProjectService(db)
    return project_service.add_project_member(
        project_id=project_id, owner_id=current_user.id, user_id=user_id
    )


@router.delete("/{project_id}/members/{user_id}")
async def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a user from a project."""
    project_service = ProjectService(db)
    return project_service.remove_project_member(
        project_id=project_id, owner_id=current_user.id, user_id=user_id
    )
