from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.project import Project
from ..models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm.attributes import flag_modified


class ProjectService:
    def create_project(
        self,
        db: Session,
        name: str,
        description: Optional[str],
        owner_id: int,
        is_private: bool = False,
        settings: Optional[Dict[str, Any]] = None
    ) -> Project:
        """Create a new project"""
        # Verify owner exists
        owner = db.query(User).filter(User.id == owner_id).first()
        if not owner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project owner not found"
            )

        project = Project()
        project.name = name
        project.description = description
        project.owner_id = owner_id
        project.is_private = is_private
        project.settings = settings or {}
        project.allowed_users = [owner_id]

        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def get_project(self, db: Session, project_id: int, user_id: int) -> Project:
        """Get project by ID"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        if project.owner_id != user_id and user_id not in project.allowed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this project"
            )
        
        return project

    def get_user_projects(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Project]:
        """Get all projects accessible to a user"""
        return (
            db.query(Project)
            .filter(
                (Project.owner_id == user_id) |
                (Project.allowed_users.contains([user_id]))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_project(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_private: Optional[bool] = None,
        settings: Optional[Dict[str, Any]] = None
    ) -> Project:
        """Update project"""
        project = self.get_project(db, project_id, user_id)
        
        # Only project owner can update
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can update project"
            )
        
        if name is not None:
            project.name = name
        if description is not None:
            project.description = description
        if is_private is not None:
            project.is_private = is_private
        if settings is not None:
            project.settings = settings
            flag_modified(project, "settings")
        
        db.commit()
        db.refresh(project)
        return project

    def delete_project(self, db: Session, project_id: int, user_id: int) -> None:
        """Delete project"""
        project = self.get_project(db, project_id, user_id)
        
        # Only project owner can delete
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can delete project"
            )
        
        db.delete(project)
        db.commit()

    def add_project_member(
        self,
        db: Session,
        project_id: int,
        owner_id: int,
        user_id: int
    ) -> Project:
        """Add a user to project's allowed users"""
        project = self.get_project(db, project_id, owner_id)
        
        # Only project owner can add members
        if project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can add members"
            )
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user_id not in project.allowed_users:
            project.allowed_users.append(user_id)
            flag_modified(project, "allowed_users")
            db.commit()
            db.refresh(project)
        
        return project

    def remove_project_member(
        self,
        db: Session,
        project_id: int,
        owner_id: int,
        user_id: int
    ) -> Project:
        """Remove a user from project's allowed users"""
        project = self.get_project(db, project_id, owner_id)
        
        # Only project owner can remove members
        if project.owner_id != owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only project owner can remove members"
            )
        
        # Cannot remove project owner
        if user_id == project.owner_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove project owner"
            )
        
        if user_id in project.allowed_users:
            project.allowed_users.remove(user_id)
            flag_modified(project, "allowed_users")
            db.commit()
            db.refresh(project)
        
        return project
