"""Import ChatGPT conversation archives into the database."""

import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Any, Callable

from chatgpt_archive.db import init_db
from chatgpt_archive.models import Message, truncate_title


class ImportError(Exception):
    """Base exception for import errors."""

    pass


class InvalidArchiveError(ImportError):
    """Raised when archive directory or structure is invalid."""

    pass


class InvalidJSONError(ImportError):
    """Raised when JSON parsing fails."""

    pass


def find_conversations_file(archive_dir: Path) -> Path:
    """Find conversations.json in the archive directory.

    Args:
        archive_dir: Path to the extracted ChatGPT export directory

    Returns:
        Path to conversations.json

    Raises:
        InvalidArchiveError: If conversations.json not found
    """
    conversations_file = archive_dir / "conversations.json"

    if not conversations_file.exists():
        raise InvalidArchiveError(
            f"conversations.json not found in {archive_dir}. "
            "Please provide a valid ChatGPT export directory."
        )

    return conversations_file


def load_conversations_json(conversations_file: Path) -> List[Dict[str, Any]]:
    """Load and parse conversations.json.

    Args:
        conversations_file: Path to conversations.json

    Returns:
        List of conversation dictionaries

    Raises:
        InvalidJSONError: If JSON parsing fails
    """
    try:
        with open(conversations_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise InvalidJSONError(f"Expected JSON array, got {type(data).__name__}")

        return data

    except json.JSONDecodeError as e:
        raise InvalidJSONError(f"Failed to parse conversations.json: {e}") from e
    except Exception as e:
        raise InvalidJSONError(f"Error reading conversations.json: {e}") from e


def extract_messages_from_mapping(
    mapping: Dict[str, Any], conversation_db_id: int
) -> List[Message]:
    """Extract messages from OpenAI's tree-structured mapping.

    The mapping is a dict where keys are node IDs and values contain:
    - message: The actual message data
    - parent: Parent node ID
    - children: List of child node IDs

    Args:
        mapping: The mapping dictionary from OpenAI export
        conversation_db_id: Database ID of the parent conversation

    Returns:
        List of Message objects
    """
    messages = []

    for node_id, node_data in mapping.items():
        if not node_data or not node_data.get("message"):
            continue

        msg_data = node_data["message"]

        # Skip if no message content
        if not msg_data:
            continue

        # Extract author role
        author = msg_data.get("author", {})
        author_role = author.get("role", "user")

        # Extract content - join all parts if multiple
        content_data = msg_data.get("content", {})
        content_type = content_data.get("content_type", "text")
        parts = content_data.get("parts", [])

        # Join text parts, skip None/empty
        content = None
        if parts:
            text_parts = [str(p) for p in parts if p is not None]
            if text_parts:
                content = "\n".join(text_parts)

        # Extract metadata
        create_time = msg_data.get("create_time")
        weight = msg_data.get("weight", 1.0)
        metadata = msg_data.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}
        is_hidden = metadata.get("is_visually_hidden_from_conversation", False)

        # Create Message object
        message = Message(
            openai_id=node_id,
            conversation_id=conversation_db_id,
            parent_id=node_data.get("parent"),
            author_role=author_role,
            content=content,
            content_type=content_type,
            create_time=create_time,
            weight=weight if isinstance(weight, (int, float)) else 1.0,
            is_hidden=bool(is_hidden),
            metadata=metadata,
        )

        messages.append(message)

    return messages


def get_fallback_title(messages: List[Message]) -> str:
    """Get fallback title from first user message.

    Args:
        messages: List of messages

    Returns:
        First user message preview or "[Untitled]"
    """
    for msg in messages:
        if msg.author_role == "user" and msg.content:
            return truncate_title(msg.content)

    return "[Untitled]"


def insert_conversation(
    conn: sqlite3.Connection, conv_data: Dict[str, Any]
) -> Tuple[int, int]:
    """Insert or update a conversation and its messages.

    Implements idempotent upsert with intelligent merging:
    - If a conversation with the same openai_id exists, metadata is updated
      only when the incoming data is newer (based on update_time).
    - Messages are merged: existing messages are kept, new messages are added.
    - Duplicate messages (same openai_id) are skipped to avoid data loss.

    Args:
        conn: Database connection
        conv_data: Raw conversation data from JSON

    Returns:
        Tuple of (conversation_db_id, messages_inserted_count)
    """
    cursor = conn.cursor()

    # Extract conversation fields
    openai_id = conv_data.get("id") or conv_data.get("conversation_id")
    if not openai_id:
        raise ValueError("Conversation missing ID field")

    title = conv_data.get("title")
    create_time = conv_data.get("create_time")
    update_time = conv_data.get("update_time")
    model_slug = conv_data.get("default_model_slug")
    is_archived = conv_data.get("is_archived", False)

    # Parse messages from mapping first (needed for fallback title)
    mapping = conv_data.get("mapping", {})

    # Check if conversation exists
    cursor.execute(
        "SELECT id, update_time FROM conversations WHERE openai_id = ?", (openai_id,)
    )
    existing = cursor.fetchone()

    if existing:
        # Merge with existing conversation
        conv_db_id: int = existing[0]
        existing_update_time = existing[1]

        # Only update metadata if incoming data is newer or existing has no update_time
        if existing_update_time is None or (
            update_time is not None and update_time >= existing_update_time
        ):
            cursor.execute(
                """
                UPDATE conversations 
                SET title = COALESCE(?, title),
                    update_time = COALESCE(?, update_time),
                    model_slug = COALESCE(?, model_slug),
                    is_archived = ?
                WHERE id = ?
            """,
                (title, update_time, model_slug, int(is_archived), conv_db_id),
            )

        # Get existing message openai_ids for merge deduplication
        existing_msg_ids = set(
            row[0]
            for row in cursor.execute(
                "SELECT openai_id FROM messages WHERE conversation_id = ?",
                (conv_db_id,),
            ).fetchall()
        )

        # Extract new messages and only insert those not already present
        messages = extract_messages_from_mapping(mapping, conv_db_id)

        messages_inserted = 0
        for message in messages:
            if message.openai_id in existing_msg_ids:
                continue  # Skip duplicate message

            cursor.execute(
                """
                INSERT INTO messages (
                    conversation_id, openai_id, parent_id, author_role,
                    content, content_type, metadata, create_time, weight, is_hidden
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    message.conversation_id,
                    message.openai_id,
                    message.parent_id,
                    message.author_role,
                    message.content,
                    message.content_type,
                    json.dumps(message.metadata, ensure_ascii=False),
                    message.create_time,
                    message.weight,
                    int(message.is_hidden),
                ),
            )
            messages_inserted += 1

    else:
        # Insert new conversation
        cursor.execute(
            """
            INSERT INTO conversations (openai_id, title, create_time, update_time, model_slug, is_archived)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (openai_id, title, create_time, update_time, model_slug, int(is_archived)),
        )
        conv_db_id_temp = cursor.lastrowid
        if conv_db_id_temp is None:
            raise sqlite3.OperationalError("Failed to get conversation ID after insert")
        conv_db_id: int = conv_db_id_temp

        # Extract and insert all messages
        messages = extract_messages_from_mapping(mapping, conv_db_id)

        # If title is None/empty, use fallback
        if not title:
            fallback_title = get_fallback_title(messages)
            cursor.execute(
                "UPDATE conversations SET title = ? WHERE id = ?",
                (fallback_title, conv_db_id),
            )

        # Batch insert messages
        messages_inserted = 0
        for message in messages:
            cursor.execute(
                """
                INSERT INTO messages (
                    conversation_id, openai_id, parent_id, author_role,
                    content, content_type, metadata, create_time, weight, is_hidden
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    message.conversation_id,
                    message.openai_id,
                    message.parent_id,
                    message.author_role,
                    message.content,
                    message.content_type,
                    json.dumps(message.metadata, ensure_ascii=False),
                    message.create_time,
                    message.weight,
                    int(message.is_hidden),
                ),
            )
            messages_inserted += 1

    return conv_db_id, messages_inserted


def import_archive(
    archive_dir: Path,
    db_path: Path | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
    embed: bool = False,
    embed_model: str = "text-embedding-3-small",
) -> Tuple[int, int]:
    """Import ChatGPT archive into database.

    Args:
        archive_dir: Path to extracted ChatGPT export directory
        db_path: Optional database path (uses default if None)
        progress_callback: Optional function called with (current, total) for progress
        embed: Whether to generate embeddings during import (requires OpenAI API key)
        embed_model: Embedding model to use if embed=True

    Returns:
        Tuple of (conversations_imported, messages_imported)

    Raises:
        InvalidArchiveError: If archive structure is invalid
        InvalidJSONError: If JSON parsing fails
    """
    # Validate and find conversations.json
    archive_path = Path(archive_dir)
    if not archive_path.is_dir():
        raise InvalidArchiveError(f"{archive_dir} is not a directory")

    conversations_file = find_conversations_file(archive_path)

    # Load JSON data
    conversations_data = load_conversations_json(conversations_file)
    total_conversations = len(conversations_data)

    # Initialize database
    conn = init_db(db_path)

    # Set up embeddings schema if embedding was requested
    if embed:
        try:
            from chatgpt_archive.db import init_embeddings_schema

            init_embeddings_schema(conn)
        except Exception:
            pass  # Schema creation failure is non-critical

    try:
        conversations_imported = 0
        messages_imported = 0

        for i, conv_data in enumerate(conversations_data):
            try:
                conv_id, msg_count = insert_conversation(conn, conv_data)
                conversations_imported += 1
                messages_imported += msg_count

                # Report progress
                if progress_callback:
                    progress_callback(i + 1, total_conversations)

            except Exception as e:
                # Log error but continue with other conversations
                openai_id = conv_data.get("id", "unknown")
                print(f"Warning: Failed to import conversation {openai_id}: {e}")
                continue

        # Commit all changes
        conn.commit()

        # Progressive embedding: generate embeddings after import if requested
        if embed:
            try:
                from chatgpt_archive.embeddings import embed_messages

                embed_messages(conn, model=embed_model)
            except Exception:
                pass  # Embedding failure is non-critical

        return conversations_imported, messages_imported

    except Exception as e:
        conn.rollback()
        raise ImportError(f"Import failed: {e}") from e
    finally:
        conn.close()
