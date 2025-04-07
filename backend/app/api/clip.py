from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Body
from typing import List, Dict, Optional, Any, cast
import os
import json
from app.services.clip_service import CLIPService
from app.core.config import settings

router = APIRouter()
clip_service = CLIPService()


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze an image using CLIP and return its features."""
    try:
        # Save uploaded file temporarily
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Analyze image
        result = await clip_service.analyze_style(file_path, None)

        # Clean up
        os.remove(file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/find-similar")
async def find_similar_content(
    file: UploadFile = File(...), content_list: List[Dict[str, Any]] = []
):
    """Find content similar to the uploaded image from a list of content."""
    try:
        # Save uploaded file temporarily
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Find similar content
        result = await clip_service.analyze_style(file_path, None)

        # Clean up
        os.remove(file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/describe")
async def generate_description(file: UploadFile = File(...)):
    """Generate a natural language description of the image content."""
    try:
        # Save uploaded file temporarily
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Generate description
        result = await clip_service.analyze_style(file_path, None)

        # Clean up
        os.remove(file_path)

        return {"description": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-improvements")
async def suggest_improvements(file: UploadFile = File(...)):
    """Suggest improvements for the content based on CLIP analysis."""
    try:
        # Save uploaded file temporarily
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Get suggestions
        result = await clip_service.analyze_style(file_path, None)

        # Clean up
        os.remove(file_path)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-islamic-style")
async def analyze_islamic_style(file: UploadFile = File(...)):
    """Analyze an image for Islamic style characteristics."""
    try:
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        result = await clip_service.analyze_style(file_path, None)
        os.remove(file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-style")
async def analyze_style(
    file: UploadFile = File(...), style_categories: Optional[str] = Form(None)
):
    """Analyze an image for style characteristics."""
    try:
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse style categories if provided
        categories = json.loads(style_categories) if style_categories else None

        result = await clip_service.analyze_style(file_path, categories)
        os.remove(file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-style-guidelines")
async def generate_style_guidelines(
    files: List[UploadFile] = File(...), style_categories: Optional[str] = Form(None)
):
    """Generate style guidelines from multiple reference images."""
    try:
        file_paths = []
        for file in files:
            file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            file_paths.append(file_path)

        # Parse style categories if provided
        categories = json.loads(style_categories) if style_categories else None

        guidelines = await clip_service.generate_style_guidelines(
            file_paths, categories
        )

        # Clean up
        for path in file_paths:
            os.remove(path)

        return guidelines
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-variations")
async def suggest_variations(
    file: UploadFile = File(...),
    num_variations: int = Form(3),
    style_categories: Optional[str] = Form(None),
):
    """Suggest content variations while maintaining style consistency."""
    try:
        file_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Parse style categories if provided
        categories = json.loads(style_categories) if style_categories else None

        variations = await clip_service.suggest_content_variations(
            file_path, num_variations, categories
        )
        os.remove(file_path)
        return variations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-originality")
async def evaluate_originality(
    new_file: UploadFile = File(...),
    reference_files: List[UploadFile] = File(...),
    style_categories: Optional[str] = Form(None),
):
    """Evaluate how original a new piece of content is compared to references."""
    try:
        # Save new content
        new_path = os.path.join(settings.UPLOAD_FOLDER, str(new_file.filename))
        with open(new_path, "wb") as buffer:
            content = await new_file.read()
            buffer.write(content)

        # Save reference content
        ref_paths = []
        for file in reference_files:
            ref_path = os.path.join(settings.UPLOAD_FOLDER, str(file.filename))
            with open(ref_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            ref_paths.append(ref_path)

        # Parse style categories if provided
        categories = json.loads(style_categories) if style_categories else None

        evaluation = await clip_service.evaluate_content_originality(
            new_path, ref_paths, categories
        )

        # Clean up
        os.remove(new_path)
        for path in ref_paths:
            os.remove(path)

        return evaluation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
