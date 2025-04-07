from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import (
    get_current_user,
    create_access_token,
    verify_password,
    get_password_hash,
)
from app.models.user import User
from app.core.firebase import get_auth, get_firestore
from datetime import timedelta, datetime
from app.core.config import get_settings
from typing import Dict, Any, Optional
from firebase_admin import auth
from google.cloud import firestore

router = APIRouter()
settings = get_settings()


@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, Any]:
    """Login endpoint"""
    try:
        # Verify user credentials
        user = await get_current_user(form_data.username)
        if not user or not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "is_active": user.is_active,
                "is_admin": user.is_admin,
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}",
        )


@router.post("/register")
async def register(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Register new user"""
    try:
        # Create Firebase user
        auth_client = get_auth()
        user = auth_client.create_user(
            email=user_data["email"], password=user_data["password"]
        )

        # Create user in Firestore
        db = get_firestore()
        user_ref = db.collection("users").document(user.uid)
        user_ref.set(
            {
                "id": user.uid,
                "email": user_data["email"],
                "hashed_password": get_password_hash(user_data["password"]),
                "is_active": True,
                "is_admin": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
        )

        return {"message": "User created successfully", "user_id": user.uid}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration error: {str(e)}",
        )


@router.get("/me")
async def read_users_me(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get current user"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
    }
