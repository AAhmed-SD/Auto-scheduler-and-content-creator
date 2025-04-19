from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Type
from .logging import get_logger, get_audit_logger
import uuid
from datetime import datetime
from pydantic import BaseModel
from fastapi import status

logger = get_logger(__name__)
audit_logger = get_audit_logger()

class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
    code: Optional[str] = None

class BaseAPIException(HTTPException):
    """Base exception for all API errors"""
    def __init__(
        self,
        status_code: int,
        error: str,
        detail: Optional[str] = None,
        request_id: Optional[str] = None,
        code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error = error
        self.request_id = request_id
        self.code = code

class ValidationError(BaseAPIException):
    """Exception for validation errors"""
    def __init__(
        self,
        detail: str,
        request_id: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error="Validation Error",
            detail=detail,
            request_id=request_id,
            code="VALIDATION_ERROR"
        )

class AuthenticationError(BaseAPIException):
    """Exception for authentication errors"""
    def __init__(
        self,
        detail: str = "Invalid credentials",
        request_id: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="Authentication Error",
            detail=detail,
            request_id=request_id,
            code="AUTHENTICATION_ERROR"
        )

class AuthorizationError(BaseAPIException):
    """Exception for authorization errors"""
    def __init__(
        self,
        detail: str = "Insufficient permissions",
        request_id: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="Authorization Error",
            detail=detail,
            request_id=request_id,
            code="AUTHORIZATION_ERROR"
        )

class ResourceNotFoundError(BaseAPIException):
    """Exception for resource not found errors"""
    def __init__(
        self,
        resource: str,
        request_id: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="Resource Not Found",
            detail=f"{resource} not found",
            request_id=request_id,
            code="RESOURCE_NOT_FOUND"
        )

class ConflictError(BaseAPIException):
    """Exception for resource conflict errors"""
    def __init__(
        self,
        detail: str,
        request_id: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="Conflict Error",
            detail=detail,
            request_id=request_id,
            code="CONFLICT_ERROR"
        )

class ServiceError(BaseAPIException):
    """Exception for service errors"""
    def __init__(
        self,
        detail: str = "Internal server error",
        request_id: Optional[str] = None
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Service Error",
            detail=detail,
            request_id=request_id,
            code="SERVICE_ERROR"
        )

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Enhanced global error handler middleware"""
    correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
    
    if isinstance(exc, BaseAPIException):
        # Log the error with enhanced context
        logger.error(
            f"Application error: {exc.error}",
            extra={
                "error_id": exc.request_id,
                "error_code": exc.code,
                "status_code": exc.status_code,
                "details": exc.detail,
                "path": request.url.path,
                "method": request.method,
                "correlation_id": correlation_id,
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        
        # Log to audit log for security-related errors
        if exc.status_code in [401, 403]:
            audit_logger.warning(
                "Security violation",
                extra={
                    "error_id": exc.request_id,
                    "error_code": exc.code,
                    "path": request.url.path,
                    "method": request.method,
                    "client": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent")
                }
            )
            
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error,
                "error_id": exc.request_id,
                "error_code": exc.code,
                "details": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    elif isinstance(exc, HTTPException):
        # Log FastAPI HTTP exceptions with enhanced context
        logger.error(
            f"HTTP error: {exc.detail}",
            extra={
                "error_id": str(uuid.uuid4()),
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
                "correlation_id": correlation_id,
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "error_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    else:
        # Log unexpected errors with enhanced context
        logger.exception(
            "Unexpected error occurred",
            extra={
                "error_id": str(uuid.uuid4()),
                "path": request.url.path,
                "method": request.method,
                "correlation_id": correlation_id,
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent")
            }
        )
        return JSONResponse(
            status_code=500,
            content={
                "error": "An unexpected error occurred",
                "error_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat()
            }
        ) 