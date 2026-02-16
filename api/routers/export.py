"""Export endpoints."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from api.services import archive_service

router = APIRouter(tags=["Export"])

SUPPORTED_FORMATS = ["md", "json", "yaml", "html", "xml", "csv", "xlsx"]


@router.get("/api/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = Query(..., enum=SUPPORTED_FORMATS),
) -> Response:
    """Export a conversation in the specified format.

    The conversation_id can be a single ID or comma-separated IDs for batch export.
    """
    try:
        # Check if multiple IDs provided (comma-separated)
        conversation_ids = [cid.strip() for cid in conversation_id.split(",") if cid.strip()]

        if len(conversation_ids) > 1:
            # Multi-conversation export
            content, content_type, filename = archive_service.export_multiple_conversations(
                conversation_ids, format
            )
        else:
            # Single conversation export
            content, content_type, filename = archive_service.export_conversation(
                conversation_ids[0], format
            )

        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

        if isinstance(content, bytes):
            return Response(content=content, media_type=content_type, headers=headers)

        return Response(content=content, media_type=content_type, headers=headers)

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from e
        if "unsupported" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg) from e
        raise HTTPException(status_code=400, detail=error_msg) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}") from e


@router.get("/api/export/batch")
async def export_batch(
    ids: str = Query(..., description="Comma-separated conversation IDs"),
    format: str = Query(..., enum=SUPPORTED_FORMATS),
) -> Response:
    """Export multiple conversations in a single file.

    Args:
        ids: Comma-separated list of conversation IDs
        format: Export format (md, json, yaml, html, xml, csv, xlsx)
    """
    try:
        conversation_ids = [cid.strip() for cid in ids.split(",") if cid.strip()]

        if not conversation_ids:
            raise HTTPException(status_code=400, detail="No conversation IDs provided")

        content, content_type, filename = archive_service.export_multiple_conversations(
            conversation_ids, format
        )

        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

        if isinstance(content, bytes):
            return Response(content=content, media_type=content_type, headers=headers)

        return Response(content=content, media_type=content_type, headers=headers)

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from e
        raise HTTPException(status_code=400, detail=error_msg) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch export failed: {e}") from e
