from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import mock_routes

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
app.include_router(mock_routes.router)

@app.get("/")
async def root():
    return {"message": "Welcome to Auto-Scheduler API"}
