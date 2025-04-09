from fastapi import APIRouter
from .endpoints import auth, content, schedule, analytics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(schedule.router, prefix="/schedule", tags=["scheduling"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"]) 