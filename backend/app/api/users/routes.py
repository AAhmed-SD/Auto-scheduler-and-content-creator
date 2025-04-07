from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, get_admin_user
from app.models.user import User
from app.core.firebase import get_firestore
from typing import List, Dict, Any, Optional
from datetime import datetime
from google.cloud import firestore
from firebase_admin import auth

router = APIRouter()


@router.get("/", response_model=List[Dict[str, Any]])
async def read_users(
    skip: int = 0, limit: int = 100, current_user: User = Depends(get_admin_user)
) -> List[Dict[str, Any]]:
    """Get all users (admin only)"""
    try:
        db = get_firestore()
        users_ref = db.collection("users")
        users = users_ref.limit(limit).offset(skip).stream()

        return [
            {
                "id": user.id,
                "email": user.get("email"),
                "is_active": user.get("is_active"),
                "is_admin": user.get("is_admin"),
                "created_at": user.get("created_at"),
                "updated_at": user.get("updated_at"),
            }
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving users: {str(e)}",
        )


@router.get("/{user_id}", response_model=Dict[str, Any])
async def read_user(
    user_id: str, current_user: User = Depends(get_admin_user)
) -> Dict[str, Any]:
    """Get user by ID (admin only)"""
    try:
        db = get_firestore()
        user_doc = db.collection("users").document(user_id).get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user_data = user_doc.to_dict()
        return {
            "id": user_id,
            "email": user_data["email"],
            "is_active": user_data["is_active"],
            "is_admin": user_data["is_admin"],
            "created_at": user_data["created_at"],
            "updated_at": user_data["updated_at"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}",
        )


@router.put("/{user_id}", response_model=Dict[str, Any])
async def update_user(
    user_id: str,
    user_data: Dict[str, Any],
    current_user: User = Depends(get_admin_user),
) -> Dict[str, Any]:
    """Update user (admin only)"""
    try:
        db = get_firestore()
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        update_data = {
            "email": user_data.get("email", user_doc.get("email")),
            "is_active": user_data.get("is_active", user_doc.get("is_active")),
            "is_admin": user_data.get("is_admin", user_doc.get("is_admin")),
            "updated_at": datetime.utcnow(),
        }

        user_ref.update(update_data)

        return {"id": user_id, **update_data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user: {str(e)}",
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: str, current_user: User = Depends(get_admin_user)
) -> Dict[str, str]:
    """Delete user (admin only)"""
    try:
        db = get_firestore()
        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        user_ref.delete()

        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user: {str(e)}",
        )
