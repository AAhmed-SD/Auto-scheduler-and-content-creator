from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.schedule import Schedule
from ..models.content import Content
from ..models.user import User
from ..models.project import Project

class SchedulingService:
    def create_schedule(
        self,
        db: Session,
        content_id: int,
        schedule_time: datetime,
        user_id: int,
        repeat: bool = False,
        repeat_interval: Optional[str] = None
    ) -> Schedule:
        """Create a new schedule"""
        # Verify content exists and user has access
        content = db.query(Content).filter(Content.id == content_id).first()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
        
        # Verify user has access to content's project
        if content.user_id != user_id:
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
        
        schedule = Schedule(
            content_id=content_id,
            user_id=user_id,
            schedule_time=schedule_time,
            repeat=repeat,
            repeat_interval=repeat_interval
        )
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        return schedule

    def get_schedules(
        self,
        db: Session,
        user_id: int,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Schedule]:
        """Get schedules for a user within a time range"""
        query = db.query(Schedule).filter(Schedule.user_id == user_id)
        
        if start_time:
            query = query.filter(Schedule.schedule_time >= start_time)
        if end_time:
            query = query.filter(Schedule.schedule_time <= end_time)
        
        return query.all()

    def delete_schedule(
        self,
        db: Session,
        schedule_id: int,
        user_id: int
    ) -> None:
        """Delete a schedule"""
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Schedule not found"
            )
        
        # Verify user has access
        if schedule.user_id != user_id:
            content = db.query(Content).filter(Content.id == schedule.content_id).first()
            if not content:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Content not found"
                )
            project = db.query(Project).filter(Project.id == content.project_id).first()
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Project not found"
                )
            if project.owner_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User does not have access to this schedule"
                )
        
        db.delete(schedule)
        db.commit() 