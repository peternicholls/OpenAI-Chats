"""Import and progress endpoints."""

import tempfile

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from api.models.responses import ImportProgress
from api.services import archive_service

router = APIRouter(tags=["Import"])

# Maximum file size: 500MB
MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024


@router.post("/api/import", status_code=202, response_model=ImportProgress)
async def import_archive(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ZIP file containing ChatGPT export"),
) -> ImportProgress:
    """Import a ChatGPT archive from an uploaded ZIP file."""
    if not file.filename or not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")

    # Save uploaded file to temp location with size validation
    suffix = ".zip"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB",
            )
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
