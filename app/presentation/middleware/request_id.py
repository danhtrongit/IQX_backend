"""Request ID middleware."""
import uuid
import time
from typing import Dict, Tuple
from collections import defaultdict
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi import HTTPException, status

from app.core.logging import get_logger

logger = get_logger(__name__)

# Context variable for request ID
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")


def get_request_id() -> str:
    """Get current request ID."""
    return request_id_ctx.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to each request."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request_id_ctx.set(request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using in-memory storage.

    For production with multiple instances, consider using Redis.
    """

    def __init__(self, app, requests_per_minute: int = 30, requests_per_hour: int = 200):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Storage: {ip: [(timestamp, count_minute, count_hour)]}
        self._requests: Dict[str, Tuple[float, int, int]] = defaultdict(lambda: (0, 0, 0))

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        # Only apply to chat endpoint
        if not request.url.path.startswith("/api/v1/chat"):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests. Please try again later.",
                headers={"Retry-After": "60"}
            )

        response = await call_next(request)
        return response

    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if client has exceeded rate limit.

        Returns:
            True if allowed, False if rate limit exceeded
        """
        current_time = time.time()

        # Get current counts
        last_check, count_minute, count_hour = self._requests[client_ip]

        # Reset counters if time window has passed
        if current_time - last_check > 60:
            count_minute = 0
        if current_time - last_check > 3600:
            count_hour = 0

        # Increment counters
        count_minute += 1
        count_hour += 1

        # Update storage
        self._requests[client_ip] = (current_time, count_minute, count_hour)

        # Check limits
        if count_minute > self.requests_per_minute:
            return False
        if count_hour > self.requests_per_hour:
            return False

        return True

    def get_stats(self, client_ip: str) -> Dict:
        """Get rate limit stats for a client IP."""
        last_check, count_minute, count_hour = self._requests.get(
            client_ip, (0, 0, 0)
        )

        return {
            "requests_last_minute": count_minute,
            "requests_last_hour": count_hour,
            "limit_per_minute": self.requests_per_minute,
            "limit_per_hour": self.requests_per_hour,
            "last_check": last_check,
        }

