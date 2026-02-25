"""Export endpoints."""

import logging
import urllib.parse

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from api.middleware.validation import validate_conversation_id, validate_export_format
from api.services import archive_service

router = APIRouter(tags=["Export"])
logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ["md", "json", "yaml", "html", "xml", "csv", "xlsx"]
MAX_BATCH_IDS = 500


def _content_disposition(filename: str) -> str:
    """Build a RFC 5987-compliant Content-Disposition header value."""
    encoded = urllib.parse.quote(filename, safe="")
    return f"attachment; filename*=UTF-8''{encoded}"


@router.get("/api/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = Query(..., enum=SUPPORTED_FORMATS),
) -> Response:
    """Export a conversation in the specified format.

    The conversation_id can be a single ID or comma-separated IDs for batch export.
    """
    try:
        # Validate format
        validated_format = validate_export_format(format, SUPPORTED_FORMATS)

        # Check if multiple IDs provided (comma-separated)
        conversation_ids = [cid.strip() for cid in conversation_id.split(",") if cid.strip()]

        # Validate each conversation ID
        validated_ids = []
        for cid in conversation_ids:
            try:
                validated_ids.append(validate_conversation_id(cid))
            except ValueError as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid conversation ID '{cid}': {e}",
                ) from e

        if len(validated_ids) > 1:
            # Multi-conversation export
            content, content_type, filename = archive_service.export_multiple_conversations(
                validated_ids, validated_format
            )
        else:
            # Single conversation export
            content, content_type, filename = archive_service.export_conversation(
                validated_ids[0], validated_format
            )

        headers = {"Content-Disposition": _content_disposition(filename)}

        if isinstance(content, bytes):
            return Response(content=content, media_type=content_type, headers=headers)

        return Response(content=content, media_type=content_type, headers=headers)

    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from e
        if "unsupported" in error_msg.lower():
            raise HTTPException(status_code=400, detail=error_msg) from e
        raise HTTPException(status_code=400, detail=error_msg) from e
    except Exception as e:
        logger.exception("Conversation export failed")
        raise HTTPException(status_code=500, detail="Export failed") from e


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
    # Validate format
    try:
        validated_format = validate_export_format(format, SUPPORTED_FORMATS)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    conversation_ids = [cid.strip() for cid in ids.split(",") if cid.strip()]

    if not conversation_ids:
        raise HTTPException(status_code=400, detail="No conversation IDs provided")

    if len(conversation_ids) > MAX_BATCH_IDS:
        raise HTTPException(
            status_code=422,
            detail=f"Batch export is limited to {MAX_BATCH_IDS} IDs; {len(conversation_ids)} provided.",
        )

    # Validate each conversation ID
    validated_ids = []
    for cid in conversation_ids:
        try:
            validated_ids.append(validate_conversation_id(cid))
        except ValueError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid conversation ID '{cid}': {e}",
            ) from e

    try:
        content, content_type, filename = archive_service.export_multiple_conversations(
            validated_ids, validated_format
        )

        headers = {"Content-Disposition": _content_disposition(filename)}

        if isinstance(content, bytes):
            return Response(content=content, media_type=content_type, headers=headers)

        return Response(content=content, media_type=content_type, headers=headers)

    except ValueError as e:
        error_msg = str(e)
        if "not found" in error_msg.lower():
            raise HTTPException(status_code=404, detail=error_msg) from e
        raise HTTPException(status_code=400, detail=error_msg) from e
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Batch export failed")
        raise HTTPException(status_code=500, detail="Batch export failed") from e
