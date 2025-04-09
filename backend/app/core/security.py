from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import get_settings
from app.core.supabase import supabase
from passlib.context import CryptContext
import re
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

load_dotenv()

settings = get_settings()

# Password hashing context with stronger settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased rounds for better security
)

# OAuth2 scheme for user authentication
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "user": "Regular user access",
        "admin": "Admin access",
        "content": "Content management access"
    }
)

# Password complexity requirements
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
)

def validate_password_complexity(password: str) -> bool:
    """Validate password meets complexity requirements"""
    return bool(PASSWORD_PATTERN.match(password))

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user using Supabase Auth"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify token with Supabase
        user = supabase.auth.get_user(token)
        if not user:
            raise credentials_exception
        return user
    except Exception:
        raise credentials_exception

async def get_current_active_user(
    current_user = Depends(get_current_user),
):
    """Get current active user"""
    if not current_user.get("active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_admin_user(
    current_user = Depends(get_current_user)
):
    """Get admin user"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

# Rate limiting configuration
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds

# Security headers
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}

# CORS configuration
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
    "http://localhost:3000",
    "http://localhost:8000"
]

# Session configuration
SESSION_COOKIE_NAME = "session"
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_MAX_AGE = 3600  # 1 hour

# Password policy
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_NUMBERS = True
PASSWORD_REQUIRE_SPECIAL_CHARS = True
PASSWORD_BLOCK_COMMON = True

# Audit logging configuration
AUDIT_LOG_ENABLED = True
AUDIT_LOG_LEVEL = "INFO"
AUDIT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# API key configuration
API_KEY_HEADER = "X-API-Key"
API_KEY_LENGTH = 32
API_KEY_EXPIRE_DAYS = 90

# Encryption configuration
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "your-encryption-key-here")
ENCRYPTION_ALGORITHM = "AES-256-GCM"
ENCRYPTION_NONCE_LENGTH = 12
ENCRYPTION_TAG_LENGTH = 16

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
