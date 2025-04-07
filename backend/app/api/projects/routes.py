from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user
from app.models.user import User
from app.core.firebase import get_firestore
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()


@router.post("/", response_model=Dict[str, Any])
async def create_project(
    project_data: Dict[str, Any], current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new project"""
    try:
        db = get_firestore()
        project_ref = db.collection("projects").document()

        project_data.update(
            {
                "id": project_ref.id,
                "owner_id": current_user.id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True,
                "allowed_users": [current_user.id],
            }
        )

        project_ref.set(project_data)

        return project_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}",
        )


@router.get("/", response_model=List[Dict[str, Any]])
async def read_projects(
    skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all projects for current user"""
    try:
        db = get_firestore()
        projects_ref = db.collection("projects")
        projects = (
            projects_ref.where("allowed_users", "array_contains", current_user.id)
            .limit(limit)
            .offset(skip)
            .stream()
        )

        return [{"id": project.id, **project.to_dict()} for project in projects]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving projects: {str(e)}",
        )


@router.get("/{project_id}", response_model=Dict[str, Any])
async def read_project(
    project_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get project by ID"""
    try:
        db = get_firestore()
        project_doc = db.collection("projects").document(project_id).get()

        if not project_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        project_data = project_doc.to_dict()
        if current_user.id not in project_data.get("allowed_users", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this project",
            )

        return {"id": project_id, **project_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving project: {str(e)}",
        )


@router.put("/{project_id}", response_model=Dict[str, Any])
async def update_project(
    project_id: str,
    project_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Update project"""
    try:
        db = get_firestore()
        project_ref = db.collection("projects").document(project_id)
        project_doc = project_ref.get()

        if not project_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        project_data = project_doc.to_dict()
        if current_user.id not in project_data.get("allowed_users", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this project",
            )

        update_data = {**project_data, "updated_at": datetime.utcnow()}

        project_ref.update(update_data)

        return {"id": project_id, **update_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating project: {str(e)}",
        )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete project"""
    try:
        db = get_firestore()
        project_ref = db.collection("projects").document(project_id)
        project_doc = project_ref.get()

        if not project_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
            )

        project_data = project_doc.to_dict()
        if current_user.id != project_data.get("owner_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can delete this project",
            )

        project_ref.delete()

        return {"message": "Project deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}",
        )
