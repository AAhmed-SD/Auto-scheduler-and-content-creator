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
from typing import Optional, Dict, List
from jose import JWTError, jwt
import time
from .logging import get_logger, get_audit_logger
import ipaddress

load_dotenv()

settings = get_settings()

logger = get_logger(__name__)
audit_logger = get_audit_logger()

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

class SecurityMonitor:
    """Monitor and handle security-related events"""
    
    def __init__(self):
        self.failed_attempts: Dict[str, List[float]] = {}
        self.blocked_ips: Dict[str, float] = {}
        self.rate_limits: Dict[str, List[float]] = {}
        self.block_duration = 3600  # 1 hour
        self.max_failed_attempts = 5
        self.rate_limit_window = 60  # 1 minute
        self.max_requests_per_window = 100
        
    def check_ip_block(self, ip: str) -> bool:
        """Check if an IP is blocked"""
        if ip in self.blocked_ips:
            if time.time() - self.blocked_ips[ip] < self.block_duration:
                return True
            else:
                del self.blocked_ips[ip]
        return False
        
    def record_failed_attempt(self, ip: str):
        """Record a failed authentication attempt"""
        now = time.time()
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
            
        self.failed_attempts[ip].append(now)
        
        # Remove attempts older than block duration
        self.failed_attempts[ip] = [
            t for t in self.failed_attempts[ip]
            if now - t < self.block_duration
        ]
        
        # Check if IP should be blocked
        if len(self.failed_attempts[ip]) >= self.max_failed_attempts:
            self.blocked_ips[ip] = now
            audit_logger.warning(
                "IP blocked due to multiple failed attempts",
                extra={
                    "ip": ip,
                    "attempts": len(self.failed_attempts[ip]),
                    "block_duration": self.block_duration
                }
            )
            
    def check_rate_limit(self, ip: str) -> bool:
        """Check if request rate limit is exceeded"""
        now = time.time()
        if ip not in self.rate_limits:
            self.rate_limits[ip] = []
            
        # Remove requests outside the window
        self.rate_limits[ip] = [
            t for t in self.rate_limits[ip]
            if now - t < self.rate_limit_window
        ]
        
        # Add current request
        self.rate_limits[ip].append(now)
        
        # Check if rate limit is exceeded
        if len(self.rate_limits[ip]) > self.max_requests_per_window:
            audit_logger.warning(
                "Rate limit exceeded",
                extra={
                    "ip": ip,
                    "requests": len(self.rate_limits[ip]),
                    "window": self.rate_limit_window
                }
            )
            return False
            
        return True
        
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security-related event"""
        audit_logger.warning(
            f"Security event: {event_type}",
            extra=details
        )
        
    def is_suspicious_request(self, request: Request) -> bool:
        """Check if a request appears suspicious"""
        suspicious_headers = [
            "user-agent",
            "x-forwarded-for",
            "x-real-ip"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                value = request.headers[header]
                # Add your suspicious pattern checks here
                if "sql" in value.lower() or "script" in value.lower():
                    return True
                    
        return False

class SecurityMiddleware:
    """Middleware for security monitoring"""
    
    def __init__(self, app):
        self.app = app
        self.security_monitor = SecurityMonitor()
        
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host if request.client else None
        
        if client_ip:
            # Check if IP is blocked
            if self.security_monitor.check_ip_block(client_ip):
                raise HTTPException(
                    status_code=403,
                    detail="IP address blocked due to suspicious activity"
                )
                
            # Check rate limit
            if not self.security_monitor.check_rate_limit(client_ip):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests"
                )
                
            # Check for suspicious activity
            if self.security_monitor.is_suspicious_request(request):
                self.security_monitor.log_security_event(
                    "suspicious_request",
                    {
                        "ip": client_ip,
                        "path": request.url.path,
                        "method": request.method,
                        "headers": dict(request.headers)
                    }
                )
                
        response = await call_next(request)
        return response

# Initialize security monitor
security_monitor = SecurityMonitor()
