from fastapi import Request, status
from fastapi.responses import JSONResponse
from .exceptions import (
    BaseAPIException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ConflictError,
    ServiceError,
    ErrorResponse
)
from .logging import get_logger, get_audit_logger
from .monitoring import performance_monitor, database_monitor
from datetime import datetime
import traceback
import uuid
from typing import Dict, Any

logger = get_logger(__name__)
audit_logger = get_audit_logger()

class ErrorTracker:
    """Track and analyze errors for monitoring and improvement"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.error_timestamps: Dict[str, list] = {}
        self.error_contexts: Dict[str, list] = {}
        
    def track_error(self, error_type: str, context: Dict[str, Any]):
        """Track an error occurrence with context"""
        error_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Update error counts
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Store error context
        if error_type not in self.error_contexts:
            self.error_contexts[error_type] = []
        self.error_contexts[error_type].append({
            "error_id": error_id,
            "timestamp": timestamp,
            "context": context
        })
        
        # Track timestamps for rate limiting
        if error_type not in self.error_timestamps:
            self.error_timestamps[error_type] = []
        self.error_timestamps[error_type].append(timestamp)
        
        return error_id
        
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": self.error_counts,
            "recent_errors": {
                error_type: len([
                    t for t in timestamps 
                    if (datetime.utcnow() - t).total_seconds() < 3600
                ])
                for error_type, timestamps in self.error_timestamps.items()
            }
        }

error_tracker = ErrorTracker()

async def handle_validation_error(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle validation errors with enhanced tracking"""
    error_id = error_tracker.track_error(
        "validation_error",
        {
            "path": request.url.path,
            "method": request.method,
            "details": exc.detail,
            "user_id": getattr(request.state, "user_id", None)
        }
    )
    
    error_response = ErrorResponse(
        error=exc.error,
        detail=exc.detail,
        request_id=error_id,
        code=exc.code
    )
    
    # Log to audit trail for security analysis
    audit_logger.warning(
        "Validation error occurred",
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "details": exc.detail
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def handle_authentication_error(request: Request, exc: AuthenticationError) -> JSONResponse:
    """Handle authentication errors with enhanced security tracking"""
    error_id = error_tracker.track_error(
        "authentication_error",
        {
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }
    )
    
    error_response = ErrorResponse(
        error=exc.error,
        detail=exc.detail,
        request_id=error_id,
        code=exc.code
    )
    
    # Log to audit trail for security analysis
    audit_logger.warning(
        "Authentication error occurred",
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else None
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def handle_authorization_error(request: Request, exc: AuthorizationError) -> JSONResponse:
    """Handle authorization errors with enhanced security tracking"""
    error_id = error_tracker.track_error(
        "authorization_error",
        {
            "path": request.url.path,
            "method": request.method,
            "user_id": getattr(request.state, "user_id", None),
            "client_ip": request.client.host if request.client else None
        }
    )
    
    error_response = ErrorResponse(
        error=exc.error,
        detail=exc.detail,
        request_id=error_id,
        code=exc.code
    )
    
    # Log to audit trail for security analysis
    audit_logger.warning(
        "Authorization error occurred",
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "user_id": getattr(request.state, "user_id", None)
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def handle_not_found_error(request: Request, exc: ResourceNotFoundError) -> JSONResponse:
    """Handle resource not found errors with enhanced tracking"""
    error_id = error_tracker.track_error(
        "not_found_error",
        {
            "path": request.url.path,
            "method": request.method,
            "resource": exc.detail,
            "user_id": getattr(request.state, "user_id", None)
        }
    )
    
    error_response = ErrorResponse(
        error=exc.error,
        detail=exc.detail,
        request_id=error_id,
        code=exc.code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def handle_conflict_error(request: Request, exc: ConflictError) -> JSONResponse:
    """Handle conflict errors with enhanced tracking"""
    error_id = error_tracker.track_error(
        "conflict_error",
        {
            "path": request.url.path,
            "method": request.method,
            "details": exc.detail,
            "user_id": getattr(request.state, "user_id", None)
        }
    )
    
    error_response = ErrorResponse(
        error=exc.error,
        detail=exc.detail,
        request_id=error_id,
        code=exc.code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def handle_service_error(request: Request, exc: ServiceError) -> JSONResponse:
    """Handle service errors with enhanced monitoring"""
    error_id = error_tracker.track_error(
        "service_error",
        {
            "path": request.url.path,
            "method": request.method,
            "details": exc.detail,
            "user_id": getattr(request.state, "user_id", None)
        }
    )
    
    error_response = ErrorResponse(
        error=exc.error,
        detail=exc.detail,
        request_id=error_id,
        code=exc.code
    )
    
    # Log to performance monitor
    performance_monitor.log_error(
        error_type="service_error",
        error_id=error_id,
        path=request.url.path,
        method=request.method
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.dict()
    )

async def handle_generic_error(request: Request, exc: Exception) -> JSONResponse:
    """Handle generic errors with enhanced monitoring and tracking"""
    error_id = error_tracker.track_error(
        "unhandled_error",
        {
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__,
            "error_message": str(exc),
            "traceback": traceback.format_exc(),
            "user_id": getattr(request.state, "user_id", None)
        }
    )
    
    logger.error(
        f"Unhandled error: {str(exc)}",
        extra={
            "error_id": error_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )
    
    # Log to performance monitor
    performance_monitor.log_error(
        error_type="unhandled_error",
        error_id=error_id,
        path=request.url.path,
        method=request.method
    )
    
    error_response = ErrorResponse(
        error="Internal Server Error",
        detail="An unexpected error occurred",
        request_id=error_id,
        code="INTERNAL_SERVER_ERROR"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.dict()
    ) 