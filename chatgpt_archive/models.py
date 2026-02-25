"""Data models for ChatGPT archive entities."""

from dataclasses import dataclass, field
from typing import List


def truncate_title(text: str, max_length: int = 50) -> str:
    """Truncate a string to max_length, appending '...' if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


@dataclass
class Attachment:
    """Reference to a media file attached to a message.

    Attributes:
        id: Database primary key (None before insertion)
        message_id: Foreign key to parent message
        file_path: Path to the attachment file relative to archive
        file_type: MIME type or general type (image, audio, etc.)
        original_name: Original filename from the export
    """

    file_path: str
    file_type: str | None = None
    original_name: str | None = None
    id: int | None = None
    message_id: int | None = None


@dataclass
class Message:
    """A single message/turn in a conversation.

    Attributes:
        openai_id: Original node ID from OpenAI export
        author_role: One of: user, assistant, system, tool
        content: Message text content (may be None for hidden messages)
        conversation_id: Foreign key to parent conversation
        parent_id: OpenAI node ID of parent message (for tree structure)
        content_type: Type of content (text, image, etc.)
        create_time: Unix timestamp of creation
        weight: Tree weighting from OpenAI
        is_hidden: Whether message is hidden from conversation view
        id: Database primary key (None before insertion)
        attachments: List of attached files
    """

    openai_id: str
    author_role: str
    content: str | None = None
    conversation_id: int | None = None
    parent_id: str | None = None
    content_type: str = "text"
    create_time: float | None = None
    weight: float = 1.0
    is_hidden: bool = False
    id: int | None = None
    attachments: List[Attachment] = field(default_factory=list)

    def __post_init__(self):
        """Validate author_role is one of the allowed values."""
        valid_roles = {"user", "assistant", "system", "tool"}
        if self.author_role not in valid_roles:
            raise ValueError(
                f"author_role must be one of {valid_roles}, got '{self.author_role}'"
            )


@dataclass
class Conversation:
    """A complete chat session containing multiple messages.

    Attributes:
        openai_id: Original conversation ID from OpenAI export
        title: Conversation title (may be None, use fallback)
        create_time: Unix timestamp of creation
        update_time: Unix timestamp of last update
        model_slug: Model used (e.g., gpt-4, gpt-3.5-turbo)
        is_archived: Whether conversation is archived in ChatGPT
        id: Database primary key (None before insertion)
        messages: List of messages (loaded separately)
        message_count: Count of messages (for list display)
    """

    openai_id: str
    title: str | None = None
    create_time: float | None = None
    update_time: float | None = None
    model_slug: str | None = None
    is_archived: bool = False
    id: int | None = None
    messages: List[Message] = field(default_factory=list)
    message_count: int = 0

    @property
    def display_title(self) -> str:
        """Get title with fallback for untitled conversations.

        Returns:
            Title if set, first user message preview, or "[Untitled]"
        """
        if self.title:
            return self.title

        # Try to find first user message for fallback
        for msg in self.messages:
            if msg.author_role == "user" and msg.content:
                return truncate_title(msg.content)

        return "[Untitled]"
