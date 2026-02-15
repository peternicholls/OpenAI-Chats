"""Favorites management endpoints."""

from fastapi import APIRouter, HTTPException, Query

from api.models.responses import ConversationSummary, PaginatedResponse
from api.services import archive_service

router = APIRouter(tags=["Favorites"])


@router.post("/api/conversations/{conversation_id}/favorite")
async def toggle_favorite(conversation_id: str) -> dict:
    """Toggle the favorite status of a conversation."""
    conv = archive_service.get_conversation(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

    is_favorite = archive_service.toggle_favorite(conversation_id)
    return {"is_favorite": is_favorite}


@router.get("/api/favorites", response_model=PaginatedResponse)
async def list_favorites(
    sort_by: str = Query("date", enum=["date", "title", "messages"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """List favorited conversations."""
    conversations, total = archive_service.list_favorites(
        sort_by=sort_by, order=order, limit=limit, offset=offset
    )
    items = [ConversationSummary(**c) for c in conversations]
    return PaginatedResponse(total=total, offset=offset, limit=limit, items=items)
