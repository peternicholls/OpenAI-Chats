"""Import and progress endpoints."""

import os
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from api.models.responses import ImportProgress
from api.services import archive_service

router = APIRouter(tags=["Import"])

# Maximum file size: 500MB
MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024
CHUNK_SIZE_BYTES = 1024 * 1024


@router.post("/api/import", status_code=202, response_model=ImportProgress)
async def import_archive(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="ZIP file containing ChatGPT export"),
) -> ImportProgress:
    """Import a ChatGPT archive from an uploaded ZIP file."""
    if not file.filename or not file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a ZIP archive")

    tmp_path: str | None = None
    try:
        # Save upload to temp location while enforcing a hard size limit.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            tmp_path = tmp.name
            total_size = 0

            while True:
                chunk = await file.read(CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail=(
                            f"File too large. Maximum upload size is "
                            f"{MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB. "
                            f"For larger archives, use the CLI importer."
                        ),
                    )
                tmp.write(chunk)

        if not tmp_path or not zipfile.is_zipfile(tmp_path):
            raise HTTPException(
                status_code=400, detail="File must be a valid ZIP archive"
            )

        # Run import in background
        background_tasks.add_task(archive_service.import_archive_from_zip, tmp_path)

        return ImportProgress(
            status="pending",
            current=0,
            total=0,
            percent=0.0,
            message="Import queued...",
        )
    except HTTPException:
        if tmp_path and Path(tmp_path).exists():
            os.unlink(tmp_path)
        raise
    finally:
        await file.close()
