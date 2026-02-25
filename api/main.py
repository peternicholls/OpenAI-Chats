"""FastAPI application entry point for ChatGPT Archive Web UI."""

import json
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from api.middleware.cors import setup_cors
from api.middleware.logging import add_request_logging
from api.middleware.rate_limit import add_rate_limiting
from api.routers import (
    conversations,
    embeddings,
    export,
    favorites,
    health,
    progress,
    search,
    settings,
    tags,
)
from api.routers import import_ as import_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def validate_environment() -> None:
    """Validate required environment variables on startup.

    Raises:
        RuntimeError: If required variables are missing or invalid.
    """
    errors = []

    # Validate active DB path env var if provided
    db_path = os.environ.get("CHATGPT_ARCHIVE_DB") or os.environ.get("DB_PATH")
    if db_path:
        db_path_obj = Path(db_path)
        if not db_path_obj.parent.exists():
            errors.append(
                f"CHATGPT_ARCHIVE_DB/DB_PATH parent directory does not exist: {db_path_obj.parent}"
            )

    # Validate CORS_ORIGINS if provided
    cors_origins = os.environ.get("CORS_ORIGINS")
    if cors_origins:
        try:
            origins = json.loads(cors_origins)
            if not isinstance(origins, list):
                errors.append("CORS_ORIGINS must be a JSON array")
            elif not all(isinstance(o, str) for o in origins):
                errors.append("CORS_ORIGINS must contain only strings")
        except json.JSONDecodeError as e:
            errors.append(f"CORS_ORIGINS is not valid JSON: {e}")

    if errors:
        for error in errors:
            logger.error("Configuration error: %s", error)
        raise RuntimeError("Environment validation failed: " + "; ".join(errors))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown lifecycle."""
    # --- Startup ---
    validate_environment()

    # Validate schema compatibility once at startup
    from api.services.archive_service import (
        get_connection,
        validate_schema_compatibility,
    )

    try:
        conn = get_connection(validate=False)
        is_valid, errors = validate_schema_compatibility(conn)
        conn.close()
        if not is_valid:
            logger.warning("Schema compatibility issues: %s", "; ".join(errors))
    except Exception as e:
        logger.warning("Schema validation skipped (DB may not exist yet): %s", e)

    # Load settings on startup
    from api.services.settings_service import get_settings_path, load_settings

    settings_path = get_settings_path()
    try:
        load_settings()
        if settings_path.exists():
            logger.info("Settings loaded from %s", settings_path)
        else:
            logger.info("Using default settings (no settings file found)")
    except Exception as e:
        logger.warning("Failed to load settings, using defaults: %s", e)

    # Restore persisted progress state (marks interrupted jobs as 'error')
    from api.services.archive_service import load_persisted_progress

    try:
        load_persisted_progress()
    except Exception as e:
        logger.warning("Failed to load persisted progress state: %s", e)

    # Warn if binding to 0.0.0.0
    host = os.environ.get("API_HOST", "0.0.0.0")  # noqa: S104
    if host == "0.0.0.0":  # noqa: S104
        logger.warning("Security: API exposed on all interfaces (0.0.0.0)")

    yield
    # --- Shutdown (nothing to clean up currently) ---


app = FastAPI(
    title="ChatGPT Archive API",
    version="1.0.0",
    description="REST API for ChatGPT Archive Web UI",
    lifespan=lifespan,
)

# Setup CORS and security headers
setup_cors(app)

# Setup request logging (JSON format for Docker log aggregation)
add_request_logging(app)

# Setup rate limiting (100 requests/minute per IP)
add_rate_limiting(app, requests_per_minute=100)

# Include routers
app.include_router(health.router)
app.include_router(conversations.router)
app.include_router(search.router)
app.include_router(export.router)
app.include_router(tags.router)
app.include_router(favorites.router)
app.include_router(embeddings.router)
app.include_router(progress.router)
app.include_router(import_router.router)
app.include_router(settings.router)
