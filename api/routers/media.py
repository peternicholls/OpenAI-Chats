"""Media endpoints for serving archive attachments."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from api.middleware.validation import (
    validate_media_conversation_id,
    validate_media_file_id,
)
from api.services import media_service

router = APIRouter(tags=["Media"])


@router.get("/api/media/root/{file_id}")
async def get_root_media(file_id: str) -> FileResponse:
    """Serve a root-level archive file."""
    try:
        validated_file_id = validate_media_file_id(file_id, root_level=True)
        path = media_service.resolve_root_media_path(validated_file_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if path is None:
        raise HTTPException(status_code=404, detail="Media file not found in archive")

    mime_type, _filename = media_service.get_media_metadata(path)
    return FileResponse(
        path,
        media_type=mime_type,
        headers={
            "Cache-Control": "public, max-age=86400, immutable",
            "Content-Disposition": media_service.build_root_content_disposition(path),
        },
    )


@router.get("/api/media/{conv_id}/{file_id}")
async def get_conversation_media(conv_id: str, file_id: str) -> FileResponse:
    """Serve a conversation-scoped image or audio file."""
    try:
        validated_conv_id = validate_media_conversation_id(conv_id)
        validated_file_id = validate_media_file_id(file_id)
        path = media_service.resolve_conversation_media_path(
            validated_conv_id, validated_file_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if path is None:
        raise HTTPException(status_code=404, detail="Media file not found in archive")

    mime_type, _filename = media_service.get_media_metadata(path)
    return FileResponse(
        path,
        media_type=mime_type,
        headers={"Cache-Control": "public, max-age=86400, immutable"},
    )