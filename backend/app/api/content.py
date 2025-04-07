from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.services.content_service import ContentService
from app.services.auth_service import AuthService
from app.models.user import User
from app.core.config import settings

router = APIRouter()


class StyleAnalysisRequest(BaseModel):
    reference_url: str
    content_type: str
    style_elements: dict


class ContentGenerationRequest(BaseModel):
    template_id: str
    content_type: str
    quote: str
    style_adjustments: Optional[dict] = None
    music_preference: Optional[str] = None


class ScheduleRequest(BaseModel):
    content_id: str
    platforms: List[str]
    schedule: dict
    captions: dict
    hashtags: dict


class ContentResponse(BaseModel):
    content_id: str
    status: str
    estimated_time: Optional[str] = None
    preview_url: Optional[str] = None


class ScheduleResponse(BaseModel):
    schedule_id: str
    status: str
    platform_status: dict


@router.post("/analyze", response_model=dict)
async def analyze_content(
    request: StyleAnalysisRequest,
    current_user: User = Depends(
        lambda token: AuthService(get_db()).get_current_user(token)
    ),
    db: Session = Depends(get_db),
):
    content_service = ContentService(db)
    try:
        analysis = await content_service.analyze_style(
            request.reference_url, request.content_type
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    request: ContentGenerationRequest,
    current_user: User = Depends(
        lambda token: AuthService(get_db()).get_current_user(token)
    ),
    db: Session = Depends(get_db),
):
    content_service = ContentService(db)
    try:
        result = await content_service.generate_content(
            request.template_id,
            request.content_type,
            request.quote,
            request.style_adjustments,
            request.music_preference,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/schedule", response_model=ScheduleResponse)
async def schedule_content(
    request: ScheduleRequest,
    current_user: User = Depends(
        lambda token: AuthService(get_db()).get_current_user(token)
    ),
    db: Session = Depends(get_db),
):
    content_service = ContentService(db)
    try:
        result = await content_service.schedule_content(
            request.content_id,
            request.platforms,
            request.schedule,
            request.captions,
            request.hashtags,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
