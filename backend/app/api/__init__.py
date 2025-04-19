from fastapi import APIRouter
from . import mock_routes

# Create main router
router = APIRouter()

# Include mock routes
router.include_router(mock_routes.router)

# This file is intentionally left empty to mark the directory as a Python package
