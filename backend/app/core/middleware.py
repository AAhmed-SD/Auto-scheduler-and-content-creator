from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from datetime import datetime
import time
from typing import Callable
from .audit import audit_trail, AuditEvent
from .logging import get_logger, log_api_call
import uuid

logger = get_logger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log API requests and responses"""
    
    def __init__(
        self,
        app: ASGIApp,
        *,
        exclude_paths: list[str] = None,
        exclude_methods: list[str] = None
    ):
        super().__init__(app)
        self.exclude_paths = exclude_paths or []
        self.exclude_methods = exclude_methods or []
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths/methods
        if (
            request.url.path in self.exclude_paths
            or request.method in self.exclude_methods
        ):
            return await call_next(request)
            
        # Get user ID if authenticated
        user_id = None
        if hasattr(request.state, "user"):
            user_id = request.state.user.id
        
        # Start timer
        start_time = time.time()
        
        # Get request details
        request_id = request.headers.get("X-Request-ID", "unknown")
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "client_ip": client_ip,
                "user_id": user_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "headers": dict(request.headers)
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log successful request
            log_api_call(
                logger=logger,
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                user_id=user_id,
                status_code=response.status_code,
                duration=duration
            )
            
            # Log audit event
            audit_trail.log_event(
                AuditEvent(
                    timestamp=datetime.now(),
                    event_type="api_request",
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    details={
                        "request_id": request_id,
                        "client_ip": client_ip,
                        "status_code": response.status_code,
                        "duration": duration
                    },
                    ip_address=client_ip,
                    status="success" if response.status_code < 400 else "error"
                )
            )
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            
            # Log failed request
            log_api_call(
                logger=logger,
                request_id=request_id,
                path=request.url.path,
                method=request.method,
                user_id=user_id,
                duration=duration,
                error=str(e),
                stack_trace=str(e.__traceback__)
            )
            
            # Log audit event
            audit_trail.log_event(
                AuditEvent(
                    timestamp=datetime.now(),
                    event_type="api_request",
                    user_id=user_id,
                    action=f"{request.method} {request.url.path}",
                    details={
                        "request_id": request_id,
                        "client_ip": client_ip,
                        "status_code": response.status_code,
                        "duration": duration
                    },
                    ip_address=client_ip,
                    status="error"
                )
            )
            
            raise

class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add a unique request ID to each request"""
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response 