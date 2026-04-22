"""Pydantic response models for the ChatGPT Archive API."""

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class ConversationSummary(BaseModel):
    """Conversation list item."""

    id: str = Field(..., description="OpenAI conversation ID")
    title: str | None = Field(None, description="Conversation title")
    create_time: float | None = Field(None, description="Unix timestamp")
    update_time: float | None = Field(None, description="Unix timestamp")
    message_count: int = Field(..., description="Number of messages")
    model: str | None = Field(None, description="Model used")
    tags: list[str] = Field(default_factory=list, description="Associated tags")
    is_favorite: bool = Field(False, description="Whether conversation is favorited")


class MarkdownSegment(BaseModel):
    """Markdown or plain-text prose segment."""

    kind: Literal["markdown"]
    text: str = Field(..., min_length=1, description="Markdown source text for display")
    attachment_index: None = Field(None, description="Unused for markdown segments")
    fallback_label: None = Field(None, description="Unused for markdown segments")


class AttachmentSegment(BaseModel):
    """Attachment reference segment."""

    kind: Literal["attachment"]
    text: None = Field(None, description="Unused for attachment segments")
    attachment_index: int = Field(
        ..., ge=0, description="Index into the message attachments array"
    )
    fallback_label: None = Field(None, description="Unused for attachment segments")


class FallbackSegment(BaseModel):
    """Readable fallback for unsupported structured content."""

    kind: Literal["fallback"]
    text: str = Field(..., min_length=1, description="Readable fallback body")
    attachment_index: None = Field(None, description="Unused for fallback segments")
    fallback_label: str = Field(..., min_length=1, description="Short fallback label")


class ThinkingSegment(BaseModel):
    """Collapsed indicator for AI reasoning/search activity."""

    kind: Literal["thinking"]
    activity_type: Literal["reasoning", "search", "both"] = Field(
        ..., description="Type of AI activity: reasoning, search, or both"
    )
    text: None = Field(None, description="Unused for thinking segments")
    attachment_index: None = Field(None, description="Unused for thinking segments")
    fallback_label: None = Field(None, description="Unused for thinking segments")


RenderSegment = Annotated[
    MarkdownSegment | AttachmentSegment | FallbackSegment | ThinkingSegment,
    Field(discriminator="kind"),
]


class Attachment(BaseModel):
    """Resolved media attachment."""

    type: str = Field(..., description="Attachment type: image, audio, file")
    url: str = Field(..., description="Relative API URL to retrieve the attachment")
    filename: str = Field(..., description="Attachment filename")
    mime_type: str | None = Field(None, description="Detected MIME type")
    width: int | None = Field(None, description="Image width in pixels")
    height: int | None = Field(None, description="Image height in pixels")
    size_bytes: int | None = Field(None, description="Attachment size in bytes")
    found: bool = Field(..., description="Whether the attachment exists on disk")


class Message(BaseModel):
    """Single message in a conversation."""

    id: str = Field(..., description="OpenAI message ID")
    role: str = Field(..., description="author role: user, assistant, system, tool")
    content: str | None = Field(None, description="Message content")
    create_time: float | None = Field(None, description="Unix timestamp")
    attachments: list[Attachment] = Field(
        default_factory=list, description="Resolved media attachments"
    )
    segments: list[RenderSegment] = Field(
        default_factory=list, description="Ordered renderable content segments"
    )


class ConversationDetail(BaseModel):
    """Full conversation with messages."""

    id: str
    title: str | None
    create_time: float | None
    update_time: float | None
    model: str | None
    message_count: int
    visible_message_count: int | None = None
    messages: list[Message]
    tags: list[str] = Field(default_factory=list)
    is_favorite: bool = False


class SearchResult(BaseModel):
    """Search result item with preview."""

    conversation_id: str
    title: str | None
    create_time: float | None
    match_count: int = Field(..., description="Number of matching messages")
    preview: str = Field(..., description="Snippet of matching content")
    relevance_score: float | None = Field(None, description="For semantic search")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    total: int
    offset: int
    limit: int
    items: list


class Tag(BaseModel):
    """Tag with usage count."""

    name: str
    count: int = Field(..., description="Number of conversations with this tag")


class ImportProgress(BaseModel):
    """Real-time import progress."""

    status: str = Field(..., description="pending, processing, complete, error")
    current: int = Field(0, description="Conversations processed")
    total: int = Field(0, description="Total conversations")
    percent: float = Field(0.0, description="Completion percentage")
    message: str | None = Field(None, description="Status message")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = Field(None, description="Additional context")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    database: str = "connected"
