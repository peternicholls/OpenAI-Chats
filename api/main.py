"""FastAPI application entry point for ChatGPT Archive Web UI."""

import json
import logging
import os
import sys
from pathlib import Path

from fastapi import FastAPI

from api.middleware.cors import setup_cors
from api.routers import health, conversations, search, export, tags, favorites, embeddings, progress, import_ as import_router, settings
from api.services.settings_service import load_settings, get_settings_path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def validate_environment() -> None:
    """Validate required environment variables on startup.

    Raises:
        SystemExit: If required variables are missing or invalid.
    """
    errors = []

    # Validate DB_PATH if provided
    db_path = os.environ.get("DB_PATH")
    if db_path:
        db_path_obj = Path(db_path)
        if not db_path_obj.parent.exists():
            errors.append(f"DB_PATH parent directory does not exist: {db_path_obj.parent}")

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
        sys.exit(1)


# Validate environment on module load
validate_environment()

app = FastAPI(
    title="ChatGPT Archive API",
    version="1.0.0",
    description="REST API for ChatGPT Archive Web UI",
)

# Setup CORS
setup_cors(app)

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


@app.on_event("startup")
async def startup_event() -> None:
    """Load settings and log startup information."""
    # Load settings on startup
    settings_path = get_settings_path()
    try:
        user_settings = load_settings()
        if settings_path.exists():
            logger.info("Settings loaded from %s", settings_path)
        else:
            logger.info("Using default settings (no settings file found)")
    except Exception as e:
        logger.warning("Failed to load settings, using defaults: %s", e)

    # Warn if binding to 0.0.0.0
    host = os.environ.get("API_HOST", "0.0.0.0")
    if host == "0.0.0.0":
        logger.warning("Security: API exposed on all interfaces (0.0.0.0)")
