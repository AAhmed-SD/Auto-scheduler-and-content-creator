from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from app.core.security import get_current_user
from app.models.user import User
from app.models.schedule import Schedule
from app.services.content_service import ContentService
from app.services.scheduling_service import SchedulingService
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()
content_service = ContentService()
scheduling_service = SchedulingService()


@router.post("/schedule", response_model=Schedule)
async def schedule_content(
    content_id: int,
    schedule_time: datetime,
    repeat: bool = False,
    repeat_interval: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Schedule:
    """Schedule content for publishing"""
    try:
        # Get content and verify access
        content = content_service.get_content(db, content_id, current_user.id)

        # Create schedule
        schedule = scheduling_service.create_schedule(
            db=db,
            content_id=content.id,
            schedule_time=schedule_time,
            repeat=repeat,
            repeat_interval=repeat_interval,
            user_id=current_user.id
        )
        return schedule
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/schedules", response_model=List[Schedule])
async def get_schedules(
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Schedule]:
    """Get scheduled content within a time range"""
    try:
        return scheduling_service.get_schedules(
            db=db,
            user_id=current_user.id,
            start_time=start_time,
            end_time=end_time
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/schedule/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a schedule"""
    try:
        scheduling_service.delete_schedule(db, schedule_id, current_user.id)
        return {"message": "Schedule deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
