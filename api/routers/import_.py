"""Import and progress endpoints."""

import os
import tempfile
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks

from api.models.responses import ImportProgress
from api.services import archive_service

router = APIRouter(tags=["Import"])


@router.post("/api/import", status_code=202, response_model=ImportProgress)
async def import_archive(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ZIP file containing ChatGPT export"),
) -> ImportProgress:
    """Import a ChatGPT archive from an uploaded ZIP file."""
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")

    # Save uploaded file to temp location
    suffix = ".zip"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    # Run import in background
    background_tasks.add_task(archive_service.import_archive_from_zip, tmp_path)

    return ImportProgress(
        status="pending",
        current=0,
        total=0,
        percent=0.0,
        message="Import queued...",
    )
