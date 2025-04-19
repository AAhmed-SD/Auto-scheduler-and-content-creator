from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.models.content import ContentTemplate, ContentTemplateCreate, ContentTemplateUpdate
from app.crud.content import content_template

router = APIRouter()

@router.post("/templates/", response_model=ContentTemplate)
def create_template(
    *,
    db: Session = Depends(get_db),
    template_in: ContentTemplateCreate
):
    """
    Create a new content template.
    """
    template = content_template.create(db, obj_in=template_in)
    return template

@router.get("/templates/", response_model=List[ContentTemplate])
def read_templates(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve content templates.
    """
    templates = content_template.get_multi(db, skip=skip, limit=limit)
    return templates

@router.get("/templates/{template_id}", response_model=ContentTemplate)
def read_template(
    *,
    db: Session = Depends(get_db),
    template_id: int
):
    """
    Get a specific content template by ID.
    """
    template = content_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@router.put("/templates/{template_id}", response_model=ContentTemplate)
def update_template(
    *,
    db: Session = Depends(get_db),
    template_id: int,
    template_in: ContentTemplateUpdate
):
    """
    Update a content template.
    """
    template = content_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    template = content_template.update(db, db_obj=template, obj_in=template_in)
    return template

@router.delete("/templates/{template_id}", response_model=ContentTemplate)
def delete_template(
    *,
    db: Session = Depends(get_db),
    template_id: int
):
    """
    Delete a content template.
    """
    template = content_template.get(db, id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    template = content_template.remove(db, id=template_id)
    return template 