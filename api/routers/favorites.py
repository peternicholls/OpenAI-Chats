"""Favorites management endpoints."""

from fastapi import APIRouter, HTTPException, Query

from api.middleware.validation import (
    validate_conversation_id,
    validate_pagination,
    validate_sort_by,
    validate_sort_order,
)
from api.models.responses import ConversationSummary, PaginatedResponse
from api.services import archive_service

router = APIRouter(tags=["Favorites"])

ALLOWED_SORT_FIELDS = ["date", "title", "messages"]


@router.post("/api/conversations/{conversation_id}/favorite")
async def toggle_favorite(conversation_id: str) -> dict:
    """Toggle the favorite status of a conversation."""
    try:
        validated_id = validate_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    conv = archive_service.get_conversation(validated_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")

    is_favorite = archive_service.toggle_favorite(validated_id)
    return {"is_favorite": is_favorite}


@router.get("/api/favorites", response_model=PaginatedResponse)
async def list_favorites(
    sort_by: str = Query("date", enum=["date", "title", "messages"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> PaginatedResponse:
    """List favorited conversations."""
    # Apply validation
    validated_sort = validate_sort_by(sort_by, ALLOWED_SORT_FIELDS)
    validated_order = validate_sort_order(order)
    validated_offset, validated_limit = validate_pagination(offset, limit)

    conversations, total = archive_service.list_favorites(
        sort_by=validated_sort,
        order=validated_order,
        limit=validated_limit,
        offset=validated_offset,
    )
    items = [ConversationSummary(**c) for c in conversations]
    return PaginatedResponse(
        total=total, offset=validated_offset, limit=validated_limit, items=items
    )
