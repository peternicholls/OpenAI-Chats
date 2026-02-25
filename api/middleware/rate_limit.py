"""Rate limiting middleware for API protection."""

import ipaddress
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
        max_tracked_clients: int = 10000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_size = window_size
        self.max_tracked_clients = max_tracked_clients
        # In-memory storage: {client_ip: [(timestamp, count), ...]}
        self.request_counts: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self.last_seen: dict[str, float] = {}
        trusted_proxies_env = os.getenv("TRUSTED_PROXY_IPS", "127.0.0.1,::1")
        self.trusted_proxy_ips = {
            ip.strip() for ip in trusted_proxies_env.split(",") if ip.strip()
        }

    @staticmethod
    def _normalize_ip(candidate: str | None) -> str | None:
        """Normalize and validate an IP address string."""
        if not candidate:
            return None
        try:
            return str(ipaddress.ip_address(candidate.strip()))
        except ValueError:
            return None

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request, considering proxies."""
        direct_ip = request.client.host if request.client else None

        # Only trust forwarding headers when request comes from a known proxy.
        if direct_ip and direct_ip in self.trusted_proxy_ips:
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                client_ip = self._normalize_ip(forwarded_for.split(",")[0].strip())
                if client_ip:
                    return client_ip

            real_ip = self._normalize_ip(request.headers.get("x-real-ip"))
            if real_ip:
                return real_ip

        normalized_direct_ip = self._normalize_ip(direct_ip)
        if normalized_direct_ip:
            return normalized_direct_ip

        return "unknown"

    def _cleanup_old_entries(self, client_ip: str, current_time: float) -> None:
        """Remove entries older than the window size."""
        cutoff = current_time - self.window_size
        entries = [
            (ts, count)
            for ts, count in self.request_counts[client_ip]
            if ts > cutoff
        ]
        if entries:
            self.request_counts[client_ip] = entries
        else:
            self.request_counts.pop(client_ip, None)
            self.last_seen.pop(client_ip, None)

    def _evict_stale_clients(self, current_time: float) -> None:
        """Evict stale and oldest client buckets to cap memory usage."""
        cutoff = current_time - self.window_size
        for client_ip, seen_at in list(self.last_seen.items()):
            if seen_at <= cutoff:
                self.last_seen.pop(client_ip, None)
                self.request_counts.pop(client_ip, None)

        overflow = len(self.last_seen) - self.max_tracked_clients
        if overflow > 0:
            oldest = sorted(self.last_seen.items(), key=lambda item: item[1])[:overflow]
            for client_ip, _ in oldest:
                self.last_seen.pop(client_ip, None)
                self.request_counts.pop(client_ip, None)

    def _get_request_count(self, client_ip: str) -> int:
        """Get total request count in current window."""
        return sum(count for _, count in self.request_counts[client_ip])

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting when explicitly disabled (e.g., during tests).
        # WARNING: Never set DISABLE_RATE_LIMIT=1 in production deployments.
        if os.getenv("DISABLE_RATE_LIMIT") == "1":
            return await call_next(request)

        # Skip rate limiting for health checks
        if request.url.path == "/api/health":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        current_time = time.time()

        # Evict stale clients and bound memory.
        self._evict_stale_clients(current_time)

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
        self.last_seen[client_ip] = current_time

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
