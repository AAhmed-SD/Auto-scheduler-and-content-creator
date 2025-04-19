from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .api.v1.api import api_router
from .core.config import get_settings
from .core.logging import setup_logging, get_logger, log_api_call
from .core.exceptions import error_handler
from .core.middleware import LoggingMiddleware, RequestIDMiddleware
from .core.error_handler import (
    handle_validation_error,
    handle_authentication_error,
    handle_authorization_error,
    handle_not_found_error,
    handle_conflict_error,
    handle_service_error,
    handle_generic_error
)
from .core.exceptions import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ConflictError,
    ServiceError
)
import time
import uuid
from datetime import datetime

settings = get_settings()

# Initialize logging
logger = setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, replace with specific hosts
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add error handler
app.add_exception_handler(Exception, error_handler)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Generate correlation ID for the request
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    # Log request start
    logger.info(
        "Incoming request",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "correlation_id": correlation_id
        }
    )
    
    start_time = time.time()
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Log API call completion with performance metrics
        log_api_call(logger, request, response, duration)
        
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.exception(
            "Request failed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "duration_ms": duration * 1000,
                "correlation_id": correlation_id
            }
        )
        raise

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Add logging middleware with exclusions
app.add_middleware(
    LoggingMiddleware,
    exclude_paths=[
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health"
    ],
    exclude_methods=["OPTIONS"]
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(
        "Validation error",
        extra={
            "errors": exc.errors(),
            "path": request.url.path,
            "method": request.method,
            "correlation_id": getattr(request.state, "correlation_id", None)
        }
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat()
        },
    )

@app.get("/")
async def root():
    return {"message": "Welcome to Auto-Scheduler & Content Creator API"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup", extra={"version": settings.VERSION})

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")

# Add error handlers
app.add_exception_handler(ValidationError, handle_validation_error)
app.add_exception_handler(AuthenticationError, handle_authentication_error)
app.add_exception_handler(AuthorizationError, handle_authorization_error)
app.add_exception_handler(ResourceNotFoundError, handle_not_found_error)
app.add_exception_handler(ConflictError, handle_conflict_error)
app.add_exception_handler(ServiceError, handle_service_error)
app.add_exception_handler(Exception, handle_generic_error)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
