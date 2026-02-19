"""Conversation CRUD endpoints."""

from fastapi import APIRouter, HTTPException, Query

from api.middleware.validation import validate_conversation_id, validate_pagination, validate_sort_by, validate_sort_order
from api.models.responses import ConversationDetail, ConversationSummary, Message, PaginatedResponse
from api.services import archive_service

router = APIRouter(tags=["Conversations"])

ALLOWED_SORT_FIELDS = ["date", "title", "messages"]


@router.get("/api/conversations", response_model=PaginatedResponse)
async def list_conversations(
    sort_by: str = Query("date", enum=["date", "title", "messages"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tag: str | None = Query(None, description="Filter by tag name"),
) -> PaginatedResponse:
    """List conversations with pagination, sorting, and optional tag filtering."""
    # Apply validation
    validated_sort = validate_sort_by(sort_by, ALLOWED_SORT_FIELDS)
    validated_order = validate_sort_order(order)
    validated_offset, validated_limit = validate_pagination(offset, limit)
    
    try:
        conversations, total = archive_service.list_conversations(
            sort_by=validated_sort, order=validated_order, limit=validated_limit, offset=validated_offset, tag_filter=tag
        )
        items = [ConversationSummary(**c) for c in conversations]
        return PaginatedResponse(total=total, offset=validated_offset, limit=validated_limit, items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str) -> ConversationDetail:
    """Get a conversation by ID with all messages."""
    try:
        validated_id = validate_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    conv = archive_service.get_conversation(validated_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
    return ConversationDetail(
        id=conv["id"],
        title=conv["title"],
        create_time=conv["create_time"],
        update_time=conv["update_time"],
        model=conv["model"],
        message_count=conv["message_count"],
        messages=[Message(**m) for m in conv["messages"]],
        tags=conv["tags"],
        is_favorite=conv.get("is_favorite", False),
    )


@router.delete("/api/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str) -> None:
    """Delete a conversation by ID."""
    try:
        validated_id = validate_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    
    deleted = archive_service.delete_conversation(validated_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
