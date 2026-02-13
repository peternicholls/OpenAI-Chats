"""SSE progress stream and import progress endpoints."""

import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from api.models.responses import ImportProgress
from api.services import archive_service

router = APIRouter(tags=["Progress"])


@router.get("/api/import/progress", response_model=ImportProgress)
async def get_import_progress() -> ImportProgress:
    """Get current import progress status."""
    progress = archive_service.get_import_progress()
    return ImportProgress(**progress)


@router.get("/api/import/progress/stream")
async def stream_import_progress() -> StreamingResponse:
    """SSE stream for real-time import progress updates."""

    async def event_generator():
        last_status = None
        while True:
            progress = archive_service.get_import_progress()
            progress_json = json.dumps(progress)

            if progress_json != last_status:
                yield f"data: {progress_json}\n\n"
                last_status = progress_json

                if progress.get("status") in ("complete", "error", "idle"):
                    break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
