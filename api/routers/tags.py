"""Tag management endpoints."""

import re

from fastapi import APIRouter, HTTPException

from api.models.requests import TagRequest
from api.models.responses import Tag
from api.services import archive_service

router = APIRouter(tags=["Tags"])

# Tag validation pattern: alphanumeric, hyphens, underscores
TAG_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
MAX_TAG_LENGTH = 50


def validate_tag_name(tag_name: str) -> None:
    """Validate tag name format.

    Raises:
        HTTPException: If tag name is invalid.
    """
    if not tag_name:
        raise HTTPException(status_code=400, detail="Tag name cannot be empty")
    if len(tag_name) > MAX_TAG_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Tag name exceeds maximum length of {MAX_TAG_LENGTH} characters"
        )
    if not TAG_PATTERN.match(tag_name):
        raise HTTPException(
            status_code=400,
            detail="Tag name must contain only alphanumeric characters, hyphens, and underscores",
        )


@router.get("/api/tags", response_model=list[Tag])
async def list_tags() -> list[Tag]:
    """List all tags with conversation counts."""
    tags = archive_service.get_all_tags()
    return [Tag(**t) for t in tags]


@router.get("/api/conversations/{conversation_id}/tags", response_model=list[str])
async def get_conversation_tags(conversation_id: str) -> list[str]:
    """Get tags for a specific conversation."""
    conv = archive_service.get_conversation(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
    return archive_service.get_tags_for_conversation(conversation_id)


@router.post("/api/conversations/{conversation_id}/tags", status_code=204)
async def add_tag(conversation_id: str, request: TagRequest) -> None:
    """Add a tag to a conversation."""
    # Validate tag name format
    validate_tag_name(request.tag_name)

    result = archive_service.add_tag_to_conversation(conversation_id, request.tag_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")


@router.delete("/api/conversations/{conversation_id}/tags/{tag_name}", status_code=204)
async def remove_tag(conversation_id: str, tag_name: str) -> None:
    """Remove a tag from a conversation."""
    result = archive_service.remove_tag_from_conversation(conversation_id, tag_name)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation or tag not found")
