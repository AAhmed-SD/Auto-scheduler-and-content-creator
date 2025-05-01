from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from app.api import mock_routes
from app.core.config import settings

app = FastAPI(
    title="Auto-Scheduler API",
    description="API for the Auto-Scheduler & Content Creator platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include mock routes
app.include_router(mock_routes.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Auto-Scheduler API"}

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }
