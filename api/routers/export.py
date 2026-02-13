"""Export endpoints."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from api.services import archive_service

router = APIRouter(tags=["Export"])


@router.get("/api/conversations/{conversation_id}/export")
async def export_conversation(
    conversation_id: str,
    format: str = Query(..., enum=["md", "json", "yaml", "html", "xml", "csv", "xlsx"]),
) -> Response:
    """Export a conversation in the specified format."""
    try:
        content, content_type, filename = archive_service.export_conversation(
            conversation_id, format
        )

        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

        if isinstance(content, bytes):
            return Response(content=content, media_type=content_type, headers=headers)

        return Response(content=content, media_type=content_type, headers=headers)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
