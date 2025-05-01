import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from app.api.routers.users import router as users_router
from app.config import settings
from app.database import sessionmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from secure import StrictTransportSecurity, ReferrerPolicy, XContentTypeOptions, XXSSProtection, CacheControl, Secure
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.debug_logs else logging.INFO)

# Security headers
secure_headers = Secure(
    hsts=StrictTransportSecurity().include_subdomains().preload().max_age(31536000),
    referrer=ReferrerPolicy().no_referrer(),
    cache=CacheControl().no_cache().no_store().must_revalidate(),
    xfo=None,  # X-Frame-Options - Configured per endpoint when needed
    xxp=XXSSProtection().enable(),
    content_type=XContentTypeOptions().nosniff(),
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    # Initialize rate limiter
    redis_client = redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_client)
    
    yield
    
    if sessionmanager._engine is not None:
        # Close the DB connection
        await sessionmanager.close()
    # Close Redis connection
    await redis_client.close()

app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs")

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure based on your deployment
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="session",
    max_age=1800,  # 30 minutes
    same_site="lax",
    https_only=True
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    max_age=600,
)

# Add security headers middleware
@app.middleware("http")
async def add_secure_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.framework.fastapi(response)
    return response

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests"}
        )

@app.get("/")
@RateLimiter(times=10, minutes=1)
async def root():
    return {"message": "Hello World"}

# Routers
app.include_router(users_router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        reload=True,
        port=8000,
        ssl_keyfile=settings.ssl_keyfile,
        ssl_certfile=settings.ssl_certfile
    ) 