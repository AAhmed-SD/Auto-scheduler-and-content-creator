from typing import Dict, Any, Optional, List, cast
from app.core.config import settings
from app.models.content import Content, ContentType, ContentStatus
from sqlalchemy.orm import Session
import openai
import json
import requests
from datetime import datetime
from fastapi import HTTPException, status
from app.models.user import User
from app.models.project import Project
from sqlalchemy.orm.attributes import flag_modified


class ContentService:
    def __init__(self, db: Session):
        self.db = db
        openai.api_key = settings.OPENAI_API_KEY

    async def analyze_style(
        self, reference_url: str, content_type: str
    ) -> Dict[str, Any]:
        """
        Analyze the style of a reference content
        """
        try:
            # TODO: Implement actual style analysis using computer vision
            # This is a placeholder implementation
            return {
                "shot_composition": ["wide", "close-up"],
                "color_palette": ["#FF0000", "#00FF00"],
                "transition_style": "fade",
                "text_animation": "fade-in",
                "music_tempo": "slow",
            }
        except Exception as e:
            raise Exception(f"Style analysis failed: {str(e)}")

    async def generate_content(
        self,
        template_id: str,
        content_type: str,
        quote: str,
        style_adjustments: Optional[Dict[str, Any]] = None,
        music_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate content based on template and style
        """
        try:
            # TODO: Implement actual content generation
            # This is a placeholder implementation
            content_type_enum = ContentType.VIDEO if content_type == "video" else ContentType.IMAGE
            
            content = Content(
                title=f"Generated Content - {datetime.now()}",
                description=quote,
                content_type=content_type_enum,
                status=ContentStatus.GENERATING,
                style_template=style_adjustments or {},
                metadata={
                    "template_id": template_id,
                    "music_preference": music_preference,
                },
            )

            self.db.add(content)
            self.db.commit()
            self.db.refresh(content)

            return {
                "content_id": content.id,
                "status": content.status.value,
                "estimated_time": "5 minutes",
                "preview_url": None,  # Will be updated when generation is complete
            }
        except Exception as e:
            raise Exception(f"Content generation failed: {str(e)}")

    async def schedule_content(
        self,
        content_id: int,
        platforms: List[str],
        schedule: Dict[str, Any],
        captions: Dict[str, str],
        hashtags: Dict[str, List[str]],
    ) -> Dict[str, Any]:
        """
        Schedule content for publishing on various platforms
        """
        try:
            content = self.db.query(Content).filter(Content.id == content_id).first()
            if not content:
                raise Exception("Content not found")

            # Update content status
            content.status = ContentStatus.SCHEDULED
            self.db.commit()

            # TODO: Implement actual scheduling logic for each platform
            platform_status: Dict[str, str] = {}
            for platform in platforms:
                platform_status[platform] = "scheduled"

            return {
                "schedule_id": f"schedule_{content_id}",
                "status": "scheduled",
                "platform_status": platform_status,
            }
        except Exception as e:
            raise Exception(f"Scheduling failed: {str(e)}")

    def create_content(
        self,
        db: Session,
        title: str,
        content_type: str,
        project_id: int,
        user_id: int,
        description: Optional[str] = None,
        media_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: ContentStatus = ContentStatus.DRAFT
    ) -> Content:
        """Create new content"""
        # Verify project exists and user has access
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

        content = Content()
        content.title = title
        content.content_type = content_type
        content.description = description
        content.media_url = media_url
        content.metadata = metadata or {}
        content.status = status
        content.project_id = project_id
        content.user_id = user_id

        db.add(content)
        db.commit()
        db.refresh(content)
        return content

    def get_content(self, db: Session, content_id: int, user_id: int) -> Content:
        """Get content by ID"""
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Verify user has access to the project
        project = db.query(Project).filter(Project.id == content.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        if project.owner_id != user_id and user_id not in project.allowed_users:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this content"
            )
        
        return content

    def get_project_content(
        self,
        db: Session,
        project_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Content]:
        """Get all content for a project"""
        # Verify project exists and user has access
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

        return (
            db.query(Content)
            .filter(Content.project_id == project_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def update_content(
        self,
        db: Session,
        content_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        media_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        status: Optional[ContentStatus] = None
    ) -> Content:
        """Update content"""
        content = self.get_content(db, content_id, user_id)
        
        if title is not None:
            content.title = title
        if description is not None:
            content.description = description
        if media_url is not None:
            content.media_url = media_url
        if metadata is not None:
            content.metadata = metadata
            flag_modified(content, "metadata")
        if status is not None:
            content.status = status
        
        db.commit()
        db.refresh(content)
        return content

    def delete_content(self, db: Session, content_id: int, user_id: int) -> None:
        """Delete content"""
        content = self.get_content(db, content_id, user_id)
        db.delete(content)
        db.commit()

    def get_scheduled_content(
        self,
        db: Session,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Content]:
        """Get scheduled content for a user"""
        # Get all projects the user has access to
        user_projects = (
            db.query(Project)
            .filter(
                (Project.owner_id == user_id) |
                (Project.allowed_users.contains([user_id]))
            )
            .all()
        )
        project_ids = [project.id for project in user_projects]

        query = db.query(Content).filter(Content.project_id.in_(project_ids))
        
        if start_time:
            query = query.filter(Content.scheduled_time >= start_time)
        if end_time:
            query = query.filter(Content.scheduled_time <= end_time)
        
        return query.all()
