"""Conversation CRUD endpoints."""

from fastapi import APIRouter, HTTPException, Query

from api.models.responses import ConversationDetail, ConversationSummary, Message, PaginatedResponse
from api.services import archive_service

router = APIRouter(tags=["Conversations"])


@router.get("/api/conversations", response_model=PaginatedResponse)
async def list_conversations(
    sort_by: str = Query("date", enum=["date", "title", "messages"]),
    order: str = Query("desc", enum=["asc", "desc"]),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    tag: str | None = Query(None, description="Filter by tag name"),
) -> PaginatedResponse:
    """List conversations with pagination, sorting, and optional tag filtering."""
    try:
        conversations, total = archive_service.list_conversations(
            sort_by=sort_by, order=order, limit=limit, offset=offset, tag_filter=tag
        )
        items = [ConversationSummary(**c) for c in conversations]
        return PaginatedResponse(total=total, offset=offset, limit=limit, items=items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/api/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str) -> ConversationDetail:
    """Get a conversation by ID with all messages."""
    conv = archive_service.get_conversation(conversation_id)
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
    deleted = archive_service.delete_conversation(conversation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
