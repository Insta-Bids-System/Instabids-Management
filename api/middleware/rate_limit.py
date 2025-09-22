import asyncio
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, requests: int = 100, period: int = 3600):
        self.requests = requests
        self.period = period  # in seconds
        self.clients: Dict[str, list] = defaultdict(list)
        self._cleanup_task = None

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Use IP address as client ID
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0]
        else:
            client_ip = request.client.host if request.client else "unknown"
        return client_ip

    def _cleanup_old_requests(self):
        """Remove expired request timestamps"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.period)

        for client_id in list(self.clients.keys()):
            self.clients[client_id] = [
                timestamp for timestamp in self.clients[client_id] if timestamp > cutoff
            ]
            if not self.clients[client_id]:
                del self.clients[client_id]

    async def check_rate_limit(self, request: Request) -> Tuple[bool, int]:
        """Check if request is within rate limit"""
        client_id = self._get_client_id(request)
        now = datetime.now()

        # Cleanup old requests periodically
        self._cleanup_old_requests()

        # Get request timestamps for this client
        timestamps = self.clients[client_id]

        # Remove old timestamps
        cutoff = now - timedelta(seconds=self.period)
        timestamps = [t for t in timestamps if t > cutoff]

        # Check if limit exceeded
        if len(timestamps) >= self.requests:
            # Calculate wait time
            oldest = min(timestamps)
            wait_time = int(
                (oldest + timedelta(seconds=self.period) - now).total_seconds()
            )
            return False, wait_time

        # Add current request
        timestamps.append(now)
        self.clients[client_id] = timestamps

        return True, 0


async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    # Skip rate limiting for health checks
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)
    # Check rate limit for auth endpoints
    if request.url.path.startswith("/api/auth"):
        from ..config import settings

        limiter = RateLimiter(
            requests=settings.rate_limit_requests, period=settings.rate_limit_period
        )

        allowed, wait_time = await limiter.check_rate_limit(request)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Try again in {wait_time} seconds",
                    "retry_after": wait_time,
                },
                headers={"Retry-After": str(wait_time)},
            )

    return await call_next(request)
