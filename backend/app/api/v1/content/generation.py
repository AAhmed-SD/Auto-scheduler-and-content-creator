from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import openai
from dotenv import load_dotenv
import os
from app.core.security import get_current_user
from app.models.user import User
from app.services.content_service import ContentService
from app.services.openai_service import OpenAIService
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.content import Content, ContentType, ContentStatus

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter()
content_service = ContentService()
openai_service = OpenAIService()


class ContentRequest(BaseModel):
    prompt: str
    content_type: str  # "text", "image", "video"
    style: Optional[str] = None
    tone: Optional[str] = None
    length: Optional[str] = None


class ContentResponse(BaseModel):
    content: str
    metadata: dict


@router.post("/generate")
async def generate_content(request: ContentRequest) -> ContentResponse:
    try:
        if request.content_type == "text":
            response = await generate_text_content(request)
        elif request.content_type == "image":
            response = await generate_image_content(request)
        else:
            raise HTTPException(status_code=400, detail="Unsupported content type")

        return ContentResponse(
            content=response["content"], metadata=response["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_text_content(request: ContentRequest) -> dict:
    try:
        # Construct the prompt with style and tone
        prompt = f"""
        Generate {request.content_type} content with the following specifications:
        - Style: {request.style or 'professional'}
        - Tone: {request.tone or 'neutral'}
        - Length: {request.length or 'medium'}
        
        Content prompt: {request.prompt}
        """

        # Call OpenAI API
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional content creator.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        return {
            "content": response.choices[0].message.content,
            "metadata": {
                "model": "gpt-4",
                "tokens": response.usage.total_tokens,
                "style": request.style,
                "tone": request.tone,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating text content: {str(e)}"
        )


async def generate_image_content(request: ContentRequest) -> dict:
    try:
        # Call OpenAI DALL-E API
        response = await openai.Image.acreate(
            prompt=request.prompt, n=1, size="1024x1024"
        )

        return {
            "content": response.data[0].url,
            "metadata": {
                "model": "dall-e-3",
                "size": "1024x1024",
                "style": request.style,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating image content: {str(e)}"
        )


@router.post("/analyze-style")
async def analyze_style(content: str) -> dict:
    try:
        # Analyze content style using GPT-4
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a content style analyzer."},
                {
                    "role": "user",
                    "content": f"Analyze the style of this content: {content}",
                },
            ],
            temperature=0.3,
            max_tokens=500,
        )

        return {
            "analysis": response.choices[0].message.content,
            "metadata": {"model": "gpt-4", "tokens": response.usage.total_tokens},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing style: {str(e)}")


@router.post("/optimize")
async def optimize_content(content: str, target_platform: str) -> dict:
    try:
        # Optimize content for specific platform
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a content optimizer for {target_platform}.",
                },
                {
                    "role": "user",
                    "content": f"Optimize this content for {target_platform}: {content}",
                },
            ],
            temperature=0.5,
            max_tokens=1000,
        )

        return {
            "optimized_content": response.choices[0].message.content,
            "metadata": {
                "model": "gpt-4",
                "platform": target_platform,
                "tokens": response.usage.total_tokens,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error optimizing content: {str(e)}"
        )


@router.post("/generate/text", response_model=Content)
async def generate_text_content(
    prompt: str,
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Content:
    """Generate text content using OpenAI"""
    try:
        # Generate content using OpenAI
        generated_text = await openai_service.generate_text(prompt)
        
        # Create content record
        content = content_service.create_content(
            db=db,
            title=f"Generated Text: {prompt[:30]}...",
            content_type=ContentType.TEXT,
            project_id=project_id,
            user_id=current_user.id,
            description=generated_text,
            status=ContentStatus.DRAFT
        )
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/generate/image", response_model=Content)
async def generate_image_content(
    prompt: str,
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Content:
    """Generate image content using OpenAI DALL-E"""
    try:
        # Generate image using OpenAI
        image_url = await openai_service.generate_image(prompt)
        
        # Create content record
        content = content_service.create_content(
            db=db,
            title=f"Generated Image: {prompt[:30]}...",
            content_type=ContentType.IMAGE,
            project_id=project_id,
            user_id=current_user.id,
            description=prompt,
            media_url=image_url,
            status=ContentStatus.DRAFT
        )
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/enhance", response_model=Content)
async def enhance_content(
    content_id: int,
    enhancement_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Content:
    """Enhance existing content"""
    try:
        # Get existing content
        content = content_service.get_content(db, content_id, current_user.id)
        
        # Generate enhancement using OpenAI
        enhanced_text = await openai_service.enhance_content(
            content.description,
            enhancement_type
        )
        
        # Update content
        updated_content = content_service.update_content(
            db=db,
            content_id=content_id,
            user_id=current_user.id,
            description=enhanced_text
        )
        return updated_content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/variations", response_model=Content)
async def generate_content_variations(
    content_id: int,
    num_variations: int = 3,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Content:
    """Generate variations of existing content"""
    try:
        # Get existing content
        content = content_service.get_content(db, content_id, current_user.id)
        
        # Generate variations using OpenAI
        variations = await openai_service.generate_variations(
            content.description,
            num_variations
        )
        
        # Create new content for each variation
        variation_contents = []
        for i, variation in enumerate(variations):
            variation_content = content_service.create_content(
                db=db,
                title=f"{content.title} - Variation {i+1}",
                content_type=content.content_type,
                project_id=content.project_id,
                user_id=current_user.id,
                description=variation,
                media_url=content.media_url,
                status=ContentStatus.DRAFT
            )
            variation_contents.append(variation_content)
        
        return variation_contents[0]  # Return first variation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
