from fastapi import HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
from typing import Dict, List, Optional
from app.core.config import get_settings
from datetime import datetime

settings = get_settings()


class RateLimiter:
    def __init__(self) -> None:
        self.requests: Dict[str, List[float]] = {}
        self.cleanup_interval: int = 60  # seconds

    async def __call__(self, request: Request) -> None:
        """Rate limiting middleware"""
        try:
            client_ip = request.client.host
            if client_ip is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not determine client IP",
                )

            current_time = time.time()

            # Clean up old entries
            self._cleanup_old_entries(current_time)

            # Check rate limit
            if client_ip in self.requests:
                if len(self.requests[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Too many requests",
                    )
                self.requests[client_ip].append(current_time)
            else:
                self.requests[client_ip] = [current_time]
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Rate limiting error: {str(e)}",
            )

    def _cleanup_old_entries(self, current_time: float) -> None:
        """Remove entries older than cleanup interval"""
        try:
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    t
                    for t in self.requests[ip]
                    if current_time - t < self.cleanup_interval
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to clean up rate limit entries: {str(e)}",
            )


rate_limiter = RateLimiter()
