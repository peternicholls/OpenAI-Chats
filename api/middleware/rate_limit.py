"""Rate limiting middleware for API protection."""

import os
import time
from collections import defaultdict
from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using a sliding window counter."""

    def __init__(
        self,
        app: FastAPI,
        requests_per_minute: int = 100,
        window_size: int = 60,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        # In-memory storage: {client_ip: [(timestamp, count), ...]}
        self.request_counts: dict[str, list[tuple[float, int]]] = defaultdict(list)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        # Check X-Forwarded-For header first (common in reverse proxy setups)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain (original client)
            return forwarded_for.split(",")[0].strip()

        # Fall back to direct client IP
        if request.client:
            return request.client.host
        return "unknown"

    def _cleanup_old_entries(self, client_ip: str, current_time: float) -> None:
        """Remove entries older than the window size."""
        cutoff = current_time - self.window_size
        self.request_counts[client_ip] = [
            (ts, count)
            for ts, count in self.request_counts[client_ip]
            if ts > cutoff
        ]

    def _get_request_count(self, client_ip: str) -> int:
        """Get total request count in current window."""
        return sum(count for _, count in self.request_counts[client_ip])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting in test mode
        if os.getenv("TESTING") == "1":
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Clean up old entries
        self._cleanup_old_entries(client_ip, current_time)

        # Check if rate limit exceeded
        request_count = self._get_request_count(client_ip)
        if request_count >= self.requests_per_minute:
            retry_after = self.window_size
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": retry_after,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + retry_after)),
                },
            )

        # Add current request to counter
        self.request_counts[client_ip].append((current_time, 1))

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        remaining = max(0, self.requests_per_minute - request_count - 1)
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(
            int(current_time + self.window_size)
        )

        return response


def add_rate_limiting(app: FastAPI, requests_per_minute: int = 100) -> None:
    """Add rate limiting middleware to the application.

    Args:
        app: FastAPI application instance.
        requests_per_minute: Maximum requests per IP per minute (default: 100).
    """
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=requests_per_minute,
    )
