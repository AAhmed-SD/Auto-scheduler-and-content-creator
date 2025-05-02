"""Collaboration routes for the application."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, List, Optional, Sequence
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from ..models.collaboration import Comment, Approval, Task, ClientShare, ContentVersion
from ..models.content import Content
from ..models.project import Project
from ..core.auth import get_current_user
from ..core.database import get_db
from ..schemas.collaboration import (
    CommentCreate, CommentResponse,
    ApprovalCreate, ApprovalResponse,
    TaskCreate, TaskResponse,
    ClientShareCreate, ClientShareResponse,
    ContentVersionResponse
)
from ..schemas.content import ContentStatus

router = APIRouter(prefix="/collaboration", tags=["collaboration"])

# Comments endpoints
@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    comment: CommentCreate,
    db: Session = Depends(get_db)
) -> CommentResponse:
    """Create a new comment"""
    try:
        db_comment = Comment(**comment.dict())
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return CommentResponse.from_orm(db_comment)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{content_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    content_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Sequence[CommentResponse]:
    """Get all comments for a content item"""
    comments = db.query(Comment).filter(
        Comment.content_item_id == content_id
    ).all()
    return [CommentResponse.from_orm(comment) for comment in comments]

# Approval endpoints
@router.post("/approvals", response_model=ApprovalResponse)
async def create_approval(
    approval: ApprovalCreate,
    db: Session = Depends(get_db)
) -> ApprovalResponse:
    """Create a new approval"""
    try:
        db_approval = Approval(**approval.dict())
        db.add(db_approval)
        db.commit()
        db.refresh(db_approval)
        return ApprovalResponse.from_orm(db_approval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Task management endpoints
@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
) -> TaskResponse:
    """Create a new task"""
    try:
        db_task = Task(**task.dict())
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return TaskResponse.from_orm(db_task)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/content/{content_id}/tasks", response_model=List[TaskResponse])
async def get_tasks(
    content_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Sequence[TaskResponse]:
    """Get all tasks for a content item"""
    tasks = db.query(Task).filter(
        Task.content_item_id == content_id
    ).all()
    return [TaskResponse.from_orm(task) for task in tasks]

# Client sharing endpoints
@router.post("/shares", response_model=ClientShareResponse)
async def create_share(
    share: ClientShareCreate,
    db: Session = Depends(get_db)
) -> ClientShareResponse:
    """Create a new client share"""
    try:
        db_share = ClientShare(**share.dict())
        db.add(db_share)
        db.commit()
        db.refresh(db_share)
        return ClientShareResponse.from_orm(db_share)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/share/{token}")
async def get_shared_content(
    token: str,
    db: Session = Depends(get_db)
) -> Dict:
    """Get content for client review using share token"""
    share = db.query(ClientShare).filter(
        ClientShare.share_token == token,
        ClientShare.is_active == True,
        ClientShare.expires_at > datetime.utcnow()
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share link not found or expired")

    # Get project content items that need review
    content_items = db.query(Content).filter(
        Content.project_id == share.project_id,
        Content.status == ContentStatus.PENDING_REVIEW
    ).all()

    return {
        "project_id": share.project_id,
        "content_items": content_items
    }

# Version control endpoints
@router.post("/content/{content_id}/versions", response_model=ContentVersionResponse)
async def create_version(
    content_id: int,
    content_data: Dict,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ContentVersionResponse:
    """Create a new version of content"""
    # Get latest version number
    latest_version = db.query(ContentVersion).filter(
        ContentVersion.content_item_id == content_id
    ).order_by(ContentVersion.version_number.desc()).first()
    
    version_number = (latest_version.version_number + 1) if latest_version else 1

    db_version = ContentVersion(
        content_item_id=content_id,
        version_number=version_number,
        content_data=content_data,
        created_by_id=current_user.id
    )
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    return ContentVersionResponse.from_orm(db_version)

@router.get("/content/{content_id}/versions", response_model=List[ContentVersionResponse])
async def get_versions(
    content_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Sequence[ContentVersionResponse]:
    """Get version history for content"""
    versions = db.query(ContentVersion).filter(
        ContentVersion.content_item_id == content_id
    ).order_by(ContentVersion.version_number.desc()).all()
    return [ContentVersionResponse.from_orm(version) for version in versions] 