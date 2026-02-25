"""Batch embedding generation for semantic search using OpenAI API.

Generates vector embeddings for messages and stores them in the database
for semantic similarity search. Supports batching, progress tracking,
and resumption of interrupted embedding jobs.
"""

import os
import sqlite3
import time
from dataclasses import dataclass
from typing import Callable, List, Tuple

from chatgpt_archive.db import (
    get_embedding_stats,
    init_embeddings_schema,
    serialize_embedding,
    EMBEDDING_DIMENSIONS,
)


# OpenAI API configuration
DEFAULT_MODEL = "text-embedding-3-small"
DEFAULT_BATCH_SIZE = 100  # Messages per API call (max 2048 for OpenAI)
MAX_TOKENS_PER_BATCH = 8000  # Approximate token budget per batch

# Pricing per 1M tokens (as of 2025)
PRICING = {
    "text-embedding-3-small": 0.020,  # $0.02 per 1M tokens
    "text-embedding-3-large": 0.130,  # $0.13 per 1M tokens
}


class EmbeddingError(Exception):
    """Raised when embedding generation fails."""

    pass


class APIKeyMissingError(EmbeddingError):
    """Raised when OpenAI API key is not configured."""

    pass


@dataclass
class EmbeddingProgress:
    """Progress tracking for embedding generation.

    Attributes:
        total: Total messages to embed
        completed: Messages embedded so far
        remaining: Messages still to embed
        tokens_used: Approximate tokens consumed
        estimated_cost: Estimated cost in USD
        model: Embedding model being used
    """

    total: int
    completed: int
    remaining: int
    tokens_used: int = 0
    estimated_cost: float = 0.0
    model: str = DEFAULT_MODEL

    @property
    def percent_complete(self) -> float:
        if self.total == 0:
            return 100.0
        return round(self.completed / self.total * 100, 1)


def get_openai_client(api_key: str | None = None):
    """Get an OpenAI client instance.

    Args:
        api_key: Optional API key. Falls back to OPENAI_API_KEY env var.

    Returns:
        OpenAI client

    Raises:
        APIKeyMissingError: If no API key is available
        EmbeddingError: If openai package is not installed
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise APIKeyMissingError(
            "OPENAI_API_KEY environment variable is not set. "
            "Set it with: export OPENAI_API_KEY='your-key-here'"
        )

    try:
        from openai import OpenAI  # type: ignore[import-untyped]

        return OpenAI(api_key=api_key)
    except ImportError:
        raise EmbeddingError(
            "openai package is not installed. "
            "Install with: pip install 'chatgpt-archive[semantic]'"
        )


def estimate_cost(
    conn: sqlite3.Connection,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Estimate the cost of embedding all unembedded messages.

    Uses a rough estimate of 4 characters per token.

    Args:
        conn: Database connection
        model: Embedding model to use

    Returns:
        Dictionary with cost estimation details
    """
    # Get messages that need embedding
    cursor = conn.execute(
        """
        SELECT COUNT(*) as count, 
               COALESCE(SUM(LENGTH(content)), 0) as total_chars
        FROM messages 
        WHERE content IS NOT NULL 
          AND content != ''
          AND id NOT IN (SELECT message_id FROM message_embeddings)
    """
    )
    row = cursor.fetchone()
    message_count = row[0]
    total_chars = row[1]

    # Rough token estimate: ~4 chars per token
    estimated_tokens = total_chars // 4

    # Get price per million tokens
    price_per_million = PRICING.get(model, PRICING[DEFAULT_MODEL])
    estimated_cost = (estimated_tokens / 1_000_000) * price_per_million

    return {
        "messages_to_embed": message_count,
        "total_characters": total_chars,
        "estimated_tokens": estimated_tokens,
        "model": model,
        "price_per_million_tokens": price_per_million,
        "estimated_cost_usd": round(estimated_cost, 4),
        "estimated_cost_display": f"${estimated_cost:.2f}",
    }


def get_unembedded_messages(
    conn: sqlite3.Connection,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> List[Tuple[int, str]]:
    """Get a batch of messages that haven't been embedded yet.

    Args:
        conn: Database connection
        batch_size: Number of messages to fetch

    Returns:
        List of (message_id, content) tuples
    """
    cursor = conn.execute(
        """
        SELECT m.id, m.content
        FROM messages m
        WHERE m.content IS NOT NULL 
          AND m.content != ''
          AND m.id NOT IN (SELECT message_id FROM message_embeddings)
        ORDER BY m.id
        LIMIT ?
    """,
        (batch_size,),
    )

    return [(row[0], row[1]) for row in cursor.fetchall()]


def generate_embeddings_batch(
    client,
    texts: List[str],
    model: str = DEFAULT_MODEL,
) -> List[List[float]]:
    """Generate embeddings for a batch of texts using OpenAI API.

    Args:
        client: OpenAI client instance
        texts: List of text strings to embed
        model: Embedding model to use

    Returns:
        List of embedding vectors (each a list of floats)

    Raises:
        EmbeddingError: If API call fails
    """
    if not texts:
        return []

    try:
        # Truncate very long texts to avoid token limits
        truncated = [text[:8000] for text in texts]

        response = client.embeddings.create(
            input=truncated,
            model=model,
        )

        # Sort by index to maintain order
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]

    except Exception as e:
        raise EmbeddingError(f"Failed to generate embeddings: {e}") from e


def store_embeddings(
    conn: sqlite3.Connection,
    message_ids: List[int],
    embeddings: List[List[float]],
    model: str = DEFAULT_MODEL,
) -> int:
    """Store generated embeddings in the database.

    Args:
        conn: Database connection
        message_ids: List of message IDs
        embeddings: List of embedding vectors
        model: Embedding model used

    Returns:
        Number of embeddings stored
    """
    stored = 0
    for msg_id, embedding in zip(message_ids, embeddings):
        blob = serialize_embedding(embedding)
        conn.execute(
            """
            INSERT OR REPLACE INTO message_embeddings (message_id, embedding, model, created_at)
            VALUES (?, ?, ?, unixepoch())
        """,
            (msg_id, blob, model),
        )
        stored += 1

    conn.commit()
    return stored


def store_embeddings_vec(
    conn: sqlite3.Connection,
    message_ids: List[int],
    embeddings: List[List[float]],
) -> int:
    """Store embeddings in the sqlite-vec virtual table for fast search.

    Args:
        conn: Database connection (must have sqlite-vec loaded)
        message_ids: List of message IDs
        embeddings: List of embedding vectors

    Returns:
        Number of embeddings stored in vec table
    """
    stored = 0
    for msg_id, embedding in zip(message_ids, embeddings):
        blob = serialize_embedding(embedding)
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO vec_messages (message_id, embedding)
                VALUES (?, ?)
            """,
                (msg_id, blob),
            )
            stored += 1
        except Exception:
            # sqlite-vec table might not exist
            break

    if stored > 0:
        conn.commit()
    return stored


def embed_messages(
    conn: sqlite3.Connection,
    model: str = DEFAULT_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    progress_callback: Callable[[EmbeddingProgress], None] | None = None,
    max_batches: int | None = None,
    api_key: str | None = None,
) -> EmbeddingProgress:
    """Generate embeddings for all unembedded messages.

    Processes messages in batches, calling the progress callback after each batch.
    Supports resumption - only processes messages without existing embeddings.

    Args:
        conn: Database connection
        model: Embedding model to use
        batch_size: Messages per API call
        progress_callback: Called after each batch with progress info
        max_batches: Maximum number of batches to process (None = all)

    Returns:
        Final EmbeddingProgress with completion statistics

    Raises:
        APIKeyMissingError: If OPENAI_API_KEY is not set
        EmbeddingError: If embedding generation fails
    """
    # Ensure schema exists
    init_embeddings_schema(conn)

    # Try to load sqlite-vec for the virtual table
    from chatgpt_archive.db import load_sqlite_vec, init_vec_table

    vec_available = load_sqlite_vec(conn)
    if vec_available:
        dimensions = EMBEDDING_DIMENSIONS.get(model, 1536)
        init_vec_table(conn, dimensions)

    # Get OpenAI client (api_key takes priority over env var)
    client = get_openai_client(api_key=api_key)

    # Get total stats
    stats = get_embedding_stats(conn)
    total = stats["total_messages"]
    completed = stats["embedded_count"]
    tokens_used = 0
    batches_processed = 0

    progress = EmbeddingProgress(
        total=total,
        completed=completed,
        remaining=total - completed,
        model=model,
    )

    if progress_callback:
        progress_callback(progress)

    while True:
        if max_batches is not None and batches_processed >= max_batches:
            break

        # Get next batch
        batch = get_unembedded_messages(conn, batch_size)
        if not batch:
            break

        message_ids = [msg_id for msg_id, _ in batch]
        texts = [content for _, content in batch]

        # Generate embeddings
        embeddings = generate_embeddings_batch(client, texts, model)

        # Store in main embeddings table
        stored = store_embeddings(conn, message_ids, embeddings, model)

        # Also store in vec table if available
        if vec_available:
            store_embeddings_vec(conn, message_ids, embeddings)

        # Update progress
        completed += stored
        # Rough token estimate
        batch_chars = sum(len(t) for t in texts)
        batch_tokens = batch_chars // 4
        tokens_used += batch_tokens

        price_per_million = PRICING.get(model, PRICING[DEFAULT_MODEL])

        progress = EmbeddingProgress(
            total=total,
            completed=completed,
            remaining=total - completed,
            tokens_used=tokens_used,
            estimated_cost=round((tokens_used / 1_000_000) * price_per_million, 4),
            model=model,
        )

        if progress_callback:
            progress_callback(progress)

        batches_processed += 1

        # Small delay to avoid rate limits
        time.sleep(0.1)

    return progress


def embed_single_message(
    conn: sqlite3.Connection,
    message_id: int,
    content: str,
    client=None,
    model: str = DEFAULT_MODEL,
) -> bool:
    """Embed a single message (used during import for progressive embedding).

    Args:
        conn: Database connection
        message_id: Message database ID
        content: Message text content
        client: Optional OpenAI client (created if not provided)
        model: Embedding model to use

    Returns:
        True if embedding was generated and stored successfully
    """
    if not content or not content.strip():
        return False

    try:
        if client is None:
            client = get_openai_client()

        embeddings = generate_embeddings_batch(client, [content[:8000]], model)
        if embeddings:
            store_embeddings(conn, [message_id], embeddings, model)
            return True
    except (APIKeyMissingError, EmbeddingError):
        pass

    return False
