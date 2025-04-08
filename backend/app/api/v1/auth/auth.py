from fastapi import APIRouter, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, cast
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    get_password_hash,
    get_current_user,
    validate_password_complexity
)
from app.models.user import User
from app.services.user_service import UserService
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import Token, UserCreate, UserResponse
from app.core.rate_limit import rate_limit
from app.core.config import get_settings
from fastapi.security import SecurityScopes
import re

load_dotenv()

router = APIRouter()
settings = get_settings()

# Password complexity requirements
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
)

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    scopes: list[str] = []

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

    @validator('password')
    def validate_password(cls, v):
        if not validate_password_complexity(v):
            raise ValueError(
                "Password must contain at least 8 characters, "
                "one uppercase letter, one lowercase letter, "
                "one number and one special character"
            )
        return v

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False

@rate_limit(limit=5, period=300)  # 5 attempts per 5 minutes
@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Login endpoint with rate limiting"""
    user = await UserService.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
        scopes=form_data.scopes
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Refresh access token"""
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = await UserService.get_user_by_username(db, username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
) -> User:
    """Register new user with password validation"""
    # Check if user exists
    if await UserService.get_user_by_username(db, user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if await UserService.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = await UserService.create_user(
        db,
        username=user_data.username,
        email=user_data.email,
        password=hashed_password,
        full_name=user_data.full_name
    )
    
    return user

@router.post("/reset-password")
async def reset_password(
    email: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Request password reset"""
    user = await UserService.get_user_by_email(db, email)
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent"}
    
    reset_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    )
    
    # TODO: Send email with reset link
    return {"message": "If the email exists, a password reset link has been sent"}

@router.post("/verify-reset-token")
async def verify_reset_token(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Reset password with token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        
        user = await UserService.get_user_by_email(db, email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found"
            )
        
        hashed_password = get_password_hash(new_password)
        await UserService.update_user_password(db, user.id, hashed_password)
        
        return {"message": "Password updated successfully"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    security_scopes: SecurityScopes,
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user info with scope validation"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """Update user info"""
    return await UserService.update_user(
        db,
        current_user.id,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name
    )

@router.delete("/me")
async def delete_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Delete user account"""
    await UserService.delete_user(db, current_user.id)
    return {"message": "User deleted successfully"}

# Placeholder function - replace with actual database query
def get_user(username: str):
    # TODO: Implement database query
    return None
