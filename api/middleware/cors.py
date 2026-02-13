"""CORS middleware configuration for the API."""

import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware for the FastAPI application.

    Reads allowed origins from CORS_ORIGINS environment variable (JSON array string).
    Defaults to http://localhost:3000 for local development.

    Args:
        app: FastAPI application instance
    """
    origins_str = os.environ.get("CORS_ORIGINS", '["http://localhost:3000"]')
    try:
        origins = json.loads(origins_str)
    except (json.JSONDecodeError, TypeError):
        origins = ["http://localhost:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
