from fastapi import APIRouter
from .generation import router as generation_router
from .scheduling import router as scheduling_router
from .media import router as media_router

router = APIRouter()

# Include all content-related routers
router.include_router(
    generation_router, prefix="/generation", tags=["Content Generation"]
)

router.include_router(
    scheduling_router, prefix="/scheduling", tags=["Content Scheduling"]
)

router.include_router(media_router, prefix="/media", tags=["Media Processing"])
