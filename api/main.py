"""FastAPI application entry point for ChatGPT Archive Web UI."""

import logging
import os

from fastapi import FastAPI

from api.middleware.cors import setup_cors
from api.routers import health, conversations, search, export, tags, favorites, embeddings, progress, import_ as import_router, settings
from api.services.settings_service import load_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

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
    settings = load_settings()
    logger.info("Settings loaded from %s", settings.get("theme", "default"))

    # Warn if binding to 0.0.0.0
    host = os.environ.get("API_HOST", "0.0.0.0")
    if host == "0.0.0.0":
        logger.warning(
            "Server binding to 0.0.0.0 — accessible from all network interfaces. "
            "Use 127.0.0.1 for localhost-only access."
        )
