"""Health check router."""

from fastapi import APIRouter, HTTPException, status

from api.models.responses import HealthResponse
from api.services.archive_service import get_connection

router = APIRouter(tags=["System"])


@router.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return HealthResponse(status="ok", database="connected")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable",
        )
