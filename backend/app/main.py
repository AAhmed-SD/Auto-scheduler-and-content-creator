from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
from .api.v1.auth import router as auth_router
from .api.v1.content import router as content_router
from .api.v1.social import router as social_router
from .api.v1.email import router as email_router

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Auto Scheduler & Content Creator",
    description="API for auto scheduling and content creation",
    version="1.0.0"
)

# Configure CORS
# TODO: Configure this properly for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Auto Scheduler & Content Creator API"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(content_router, prefix="/api/v1/content", tags=["content"])
app.include_router(social_router, prefix="/api/v1/social", tags=["social"])
app.include_router(email_router, prefix="/api/v1/email", tags=["email"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
