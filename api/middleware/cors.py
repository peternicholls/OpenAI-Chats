"""CORS and security middleware configuration for the API."""

import json
import os

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers including Content Security Policy."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)

        # Content Security Policy
        # Allow 'self' for scripts/styles, Next.js requires 'unsafe-inline' for hydration
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Next.js requires these
            "style-src 'self' 'unsafe-inline'",  # Tailwind/shadcn inline styles
            "img-src 'self' data: blob:",
            "font-src 'self' data:",
            "connect-src 'self'",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "base-uri 'self'",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # Additional security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


def setup_cors(app: FastAPI) -> None:
    """Configure CORS and security middleware for the FastAPI application.

    Reads allowed origins from CORS_ORIGINS environment variable (JSON array string).
    Defaults to http://localhost:3000 and http://localhost:3001 for local development.

    Args:
        app: FastAPI application instance
    """
    origins_str = os.environ.get("CORS_ORIGINS", '["http://localhost:3000","http://localhost:3001"]')
    try:
        origins = json.loads(origins_str)
    except (json.JSONDecodeError, TypeError):
        origins = ["http://localhost:3000", "http://localhost:3001"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
