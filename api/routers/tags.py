"""Tag management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.middleware.validation import validate_conversation_id
from api.middleware.validation import validate_tag_name as validate_tag
from api.models.requests import TagRequest
from api.models.responses import Tag
from api.services import archive_service

router = APIRouter(tags=["Tags"])


class RenameTagRequest(BaseModel):
    """Request body for renaming a tag."""

    new_name: str


def validate_tag_name(tag_name: str) -> str:
    """Validate tag name format using middleware validation.

    Args:
        tag_name: Tag name to validate.

    Returns:
        Validated and normalized tag name.

    Raises:
        HTTPException: If tag name is invalid.
    """
    try:
        return validate_tag(tag_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/api/tags", response_model=list[Tag])
async def list_tags() -> list[Tag]:
    """List all tags with conversation counts."""
    tags = archive_service.get_all_tags()
    return [Tag(**t) for t in tags]


@router.get("/api/conversations/{conversation_id}/tags", response_model=list[str])
async def get_conversation_tags(conversation_id: str) -> list[str]:
    """Get tags for a specific conversation."""
    try:
        validated_id = validate_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    conv = archive_service.get_conversation(validated_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")
    return archive_service.get_tags_for_conversation(validated_id)


@router.post("/api/conversations/{conversation_id}/tags", status_code=204)
async def add_tag(conversation_id: str, request: TagRequest) -> None:
    """Add a tag to a conversation."""
    try:
        validated_id = validate_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # Validate tag name format
    validated_tag = validate_tag_name(request.tag_name)

    result = archive_service.add_tag_to_conversation(validated_id, validated_tag)
    if not result:
        raise HTTPException(status_code=404, detail=f"Conversation {conversation_id} not found")


@router.delete("/api/conversations/{conversation_id}/tags/{tag_name}", status_code=204)
async def remove_tag(conversation_id: str, tag_name: str) -> None:
    """Remove a tag from a conversation."""
    try:
        validated_id = validate_conversation_id(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    result = archive_service.remove_tag_from_conversation(validated_id, tag_name)
    if not result:
        raise HTTPException(status_code=404, detail="Conversation or tag not found")


@router.put("/api/tags/{tag_name}")
async def rename_tag(tag_name: str, request: RenameTagRequest) -> dict:
    """Rename a tag across all conversations.

    Returns 404 if the tag does not exist, 422 if the new name is invalid.
    """
    try:
        validated_new_name = validate_tag(request.new_name)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    result = archive_service.rename_tag(tag_name, validated_new_name)
    if not result:
        raise HTTPException(status_code=404, detail=f"Tag '{tag_name}' not found")
    return {"name": validated_new_name}
