from fastapi import FastAPI, status, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.core.config import settings
import os
from datetime import datetime, timedelta

app = FastAPI(
    title="Auto-Scheduler Admin",
    description="Admin interface for the Auto-Scheduler & Content Creator platform",
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

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Configure templates
templates = Jinja2Templates(directory="app/templates")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "error": exc.detail,
            "selected_account": None,
            "stats": {},
            "upcoming_content": []
        },
        status_code=exc.status_code
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "error": "An unexpected error occurred. Please try again later.",
            "selected_account": None,
            "stats": {},
            "upcoming_content": []
        },
        status_code=500
    )

@app.get("/")
async def root(request: Request):
    try:
        # Get account ID from query params, default to None
        account_id = request.query_params.get('account')
        
        # Mock selected account data
        selected_account = {
            "id": account_id or "1",
            "name": "Nike - Sports & Lifestyle",
            "logo": "https://ui-avatars.com/api/?name=Nike&background=f97316&color=fff",
            "last_post": "2 hours ago",
            "connected_platforms": ["instagram", "tiktok", "twitter", "linkedin"],
            "content_queue": 12,
            "monthly_budget": 2500
        } if account_id or not account_id else None

        # Mock performance metrics
        stats = {
            "total_reach": "2.4M",
            "reach_increase": "18",
            "engagement_rate": "4.8",
            "engagement_vs_industry": "2.1",
            "best_performing": "Video",
            "best_performing_increase": "85",
            "roi": "3.2",
            "roi_vs_target": "0.8"
        }
        
        # Mock upcoming content
        upcoming_content = [
            {
                "title": "Summer Collection Launch",
                "type": "Video Post",
                "preview_image": "https://picsum.photos/200/200",
                "platform": "instagram",
                "schedule_time": "Tomorrow at 10:00 AM",
                "status": "scheduled"
            },
            {
                "title": "Athlete Interview Series",
                "type": "Story",
                "preview_image": "https://picsum.photos/200/200",
                "platform": "tiktok",
                "schedule_time": "Today at 3:00 PM",
                "status": "in_review"
            },
            {
                "title": "Product Feature: Air Max",
                "type": "Image Carousel",
                "preview_image": "https://picsum.photos/200/200",
                "platform": "linkedin",
                "schedule_time": "Thursday at 2:00 PM",
                "status": "draft"
            },
            {
                "title": "Community Spotlight",
                "type": "Tweet Thread",
                "preview_image": "https://picsum.photos/200/200",
                "platform": "twitter",
                "schedule_time": "Friday at 11:00 AM",
                "status": "scheduled"
            }
        ]

        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "selected_account": selected_account,
                "stats": stats,
                "upcoming_content": upcoming_content,
                "error": None
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "error": str(e),
                "selected_account": None,
                "stats": {},
                "upcoming_content": []
            },
            status_code=500
        )

@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    } 