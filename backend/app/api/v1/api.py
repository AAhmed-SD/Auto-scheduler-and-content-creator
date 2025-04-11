from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, content, projects, social_media

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(social_media.router, prefix="/social-media", tags=["social-media"]) 