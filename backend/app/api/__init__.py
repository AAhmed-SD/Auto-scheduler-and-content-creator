from fastapi import APIRouter
from . import auth, users, projects, content, analytics

# Create main router
router = APIRouter()

# Include all sub-routers
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(projects.router, prefix="/projects", tags=["Projects"])
router.include_router(content.router, prefix="/content", tags=["Content"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
