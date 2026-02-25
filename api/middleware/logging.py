"""Request logging middleware for API observability."""

import ipaddress
import json
import logging
import os
import time
from datetime import UTC, datetime

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("api.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all API requests in JSON format for Docker log aggregation."""

    def __init__(self, app, **kwargs):
        super().__init__(app, **kwargs)
        trusted_proxies_env = os.getenv("TRUSTED_PROXY_IPS", "127.0.0.1,::1")
        self.trusted_proxy_ips = {
            ip.strip() for ip in trusted_proxies_env.split(",") if ip.strip()
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        """Log request details including method, path, status, and duration."""
        start_time = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Build log entry
        log_entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query) if request.url.query else None,
            "status": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent"),
        }

        # Log level based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_entry))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, trusting forwarded headers only from known proxies."""
        direct_ip = request.client.host if request.client else None

        # Only trust forwarding headers when request comes from a known proxy
        if direct_ip and direct_ip in self.trusted_proxy_ips:
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                candidate = forwarded_for.split(",")[0].strip()
                try:
                    return str(ipaddress.ip_address(candidate))
                except ValueError:
                    pass

            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                try:
                    return str(ipaddress.ip_address(real_ip.strip()))
                except ValueError:
                    pass

        if direct_ip:
            return direct_ip

        return "unknown"


def add_request_logging(app: FastAPI) -> None:
    """Add request logging middleware to the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(RequestLoggingMiddleware)
