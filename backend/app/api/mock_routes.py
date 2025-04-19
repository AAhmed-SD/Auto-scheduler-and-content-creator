from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from ..mock_data.social_media import (
    MOCK_USERS,
    CONTENT_TEMPLATES,
    generate_mock_posts,
    generate_mock_analytics
)
from ..schemas.social_media import (
    UserResponse,
    TemplateResponse,
    PostResponse,
    PostCreate,
    PostUpdate,
    AnalyticsResponse,
    MessageResponse,
    Platform,
    PostStatus
)

router = APIRouter(prefix="/mock", tags=["mock"])

@router.get("/users", response_model=List[UserResponse])
async def get_users():
    """Get all mock users"""
    return MOCK_USERS

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get a specific mock user"""
    user = next((user for user in MOCK_USERS if user.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/templates", response_model=List[TemplateResponse])
async def get_templates(
    platform: Optional[Platform] = None
):
    """Get all content templates, optionally filtered by platform"""
    if platform:
        return [t for t in CONTENT_TEMPLATES if t.platform == platform]
    return CONTENT_TEMPLATES

@router.get("/templates/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str):
    """Get a specific content template"""
    template = next((t for t in CONTENT_TEMPLATES if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.get("/posts", response_model=List[PostResponse])
async def get_posts(
    platform: Optional[Platform] = None,
    status: Optional[PostStatus] = None,
    limit: int = Query(default=10, ge=1, le=100)
):
    """Get mock posts with optional filtering"""
    posts = generate_mock_posts(limit)
    if platform:
        posts = [p for p in posts if p.platform == platform]
    if status:
        posts = [p for p in posts if p.status == status]
    return posts

@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(post_id: str):
    """Get a specific mock post"""
    posts = generate_mock_posts(1)
    post = next((p for p in posts if p.id == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/analytics", response_model=List[AnalyticsResponse])
async def get_analytics(
    days: int = Query(default=30, ge=1, le=365)
):
    """Get mock analytics data for the specified number of days"""
    return generate_mock_analytics(days)

@router.post("/posts", response_model=PostResponse)
async def create_post(post: PostCreate):
    """Create a mock post"""
    new_post = PostResponse(
        id=f"post_{len(generate_mock_posts(1))}",
        **post.model_dump(),
        status=PostStatus.SCHEDULED
    )
    return new_post

@router.put("/posts/{post_id}", response_model=PostResponse)
async def update_post(post_id: str, post: PostUpdate):
    """Update a mock post"""
    updated_post = PostResponse(
        id=post_id,
        **post.model_dump(),
        status=PostStatus.SCHEDULED
    )
    return updated_post

@router.delete("/posts/{post_id}", response_model=MessageResponse)
async def delete_post(post_id: str):
    """Delete a mock post"""
    return MessageResponse(message=f"Post {post_id} deleted successfully")

@router.get("/test", response_model=MessageResponse)
async def test_route():
    """Test endpoint"""
    return MessageResponse(message="Mock API is working") 