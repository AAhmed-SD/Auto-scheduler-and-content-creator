from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.database import get_db
from app.core.config import settings
from app.services.auth_service import AuthService
from app.models.user import User
from pydantic import BaseModel
from app.schemas.auth import Token, TokenData

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
auth_service = AuthService()


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    email: str
    full_name: Optional[str] = None
    is_active: bool

    class Config:
        orm_mode = True


@router.post("/register", response_model=User)
async def register_user(user: User, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        return auth_service.create_user(db, user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user and return access token"""
    try:
        return auth_service.authenticate_user(db, form_data.username, form_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=User)
async def get_current_user(current_user: User = Depends(auth_service.get_current_user)):
    """Get current user information"""
    return current_user


@router.put("/me", response_model=User)
async def update_current_user(
    user_update: User,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    try:
        return auth_service.update_user(db, current_user.id, user_update)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user"""
    try:
        auth_service.delete_user(db, current_user.id)
        return {"message": "User deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
