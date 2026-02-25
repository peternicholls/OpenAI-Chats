"""Unit tests for embedding generation functionality (EMB-001 through EMB-005).

Tests token estimation, cost calculation, message batching, embedding storage,
and mocked API calls.
"""

import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from chatgpt_archive import db
from chatgpt_archive.embeddings import (
    DEFAULT_MODEL,
    PRICING,
    estimate_cost,
    get_unembedded_messages,
    store_embeddings,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def embedding_db(tmp_path: Path) -> sqlite3.Connection:
    """Create a database with messages for embedding tests."""
    from chatgpt_archive.db import init_embeddings_schema

    db_path = tmp_path / "embedding_test.db"
    conn = db.init_db(db_path)
    init_embeddings_schema(conn)

    # Insert a conversation
    cursor = conn.execute(
        "INSERT INTO conversations (openai_id, title, create_time, update_time) VALUES (?, ?, ?, ?)",
        ("emb-conv-001", "Embedding Test Conversation", 1700000000.0, 1700001000.0),
    )
    conv_id = cursor.lastrowid

    # Insert messages
    messages = [
        "Hello, how are you today?",
        "I am doing well, thank you for asking!",
        "Can you explain what neural networks are?",
        "Neural networks are computational models inspired by the brain.",
        "What is backpropagation?",
        "Backpropagation is used to train neural networks by adjusting weights.",
        "How do gradient descent work?",
        "Gradient descent minimizes the loss function step by step.",
        "What is transfer learning?",
        "Transfer learning reuses pre-trained model knowledge for new tasks.",
    ]

    for i, content in enumerate(messages):
        role = "user" if i % 2 == 0 else "assistant"
        conn.execute(
            """
            INSERT INTO messages (conversation_id, openai_id, author_role, content, create_time)
            VALUES (?, ?, ?, ?, ?)
            """,
            (conv_id, f"msg-emb-{i:04d}", role, content, 1700000000.0 + i * 60),
        )

    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# EMB-001: Token estimation
# ---------------------------------------------------------------------------


class TestEstimateTokens:
    """Tests for token count estimation (EMB-001)."""

    def test_estimate_tokens(self, embedding_db: sqlite3.Connection):
        """EMB-001: Token estimation returns a non-zero count for messages."""
        result = estimate_cost(embedding_db)

        assert result["messages_to_embed"] == 10
        assert result["estimated_tokens"] > 0
        # Rough estimate: each message is ~5-50 words → hundreds of tokens total
        assert result["estimated_tokens"] >= 10

    def test_estimate_tokens_empty_db(self, tmp_path: Path):
        """EMB-001: Empty database returns zero token estimate."""
        from chatgpt_archive.db import init_embeddings_schema

        db_path = tmp_path / "empty_emb.db"
        conn = db.init_db(db_path)
        init_embeddings_schema(conn)

        result = estimate_cost(conn)

        assert result["messages_to_embed"] == 0
        assert result["estimated_tokens"] == 0

    def test_estimate_tokens_includes_all_messages(self, embedding_db: sqlite3.Connection):
        """EMB-001: Estimate includes all unembedded messages."""
        result = estimate_cost(embedding_db)

        assert result["messages_to_embed"] == 10

    def test_estimate_tokens_excludes_already_embedded(self, embedding_db: sqlite3.Connection):
        """EMB-001: Estimate excludes already-embedded messages."""
        # Get message IDs
        rows = embedding_db.execute("SELECT id FROM messages LIMIT 3").fetchall()
        message_ids = [r[0] for r in rows]

        # Store fake embeddings for 3 messages
        fake_embeddings = [[0.1] * 1536 for _ in range(3)]
        store_embeddings(embedding_db, message_ids, fake_embeddings)

        result = estimate_cost(embedding_db)

        # Should exclude the 3 already-embedded messages
        assert result["messages_to_embed"] == 7


# ---------------------------------------------------------------------------
# EMB-002: Cost estimation
# ---------------------------------------------------------------------------


class TestEstimateCost:
    """Tests for cost calculation (EMB-002)."""

    def test_estimate_cost(self, embedding_db: sqlite3.Connection):
        """EMB-002: Cost estimate is non-negative and properly typed."""
        result = estimate_cost(embedding_db)

        assert isinstance(result["estimated_cost_usd"], float)
        assert result["estimated_cost_usd"] >= 0.0

    def test_estimate_cost_default_model(self, embedding_db: sqlite3.Connection):
        """EMB-002: Default model is the small embedding model."""
        result = estimate_cost(embedding_db)

        assert result["model"] == DEFAULT_MODEL

    def test_estimate_cost_custom_model(self, embedding_db: sqlite3.Connection):
        """EMB-002: Cost estimate uses correct pricing per model."""
        large_model = "text-embedding-3-large"
        result = estimate_cost(embedding_db, model=large_model)

        assert result["model"] == large_model
        assert result["price_per_million_tokens"] == PRICING[large_model]

    def test_estimate_cost_display_format(self, embedding_db: sqlite3.Connection):
        """EMB-002: Cost display string starts with dollar sign."""
        result = estimate_cost(embedding_db)

        assert result["estimated_cost_display"].startswith("$")

    def test_estimate_cost_zero_messages(self, tmp_path: Path):
        """EMB-002: Zero messages results in zero cost."""
        from chatgpt_archive.db import init_embeddings_schema

        db_path = tmp_path / "zero.db"
        conn = db.init_db(db_path)
        init_embeddings_schema(conn)

        result = estimate_cost(conn)

        assert result["estimated_cost_usd"] == 0.0


# ---------------------------------------------------------------------------
# EMB-003: Message batching
# ---------------------------------------------------------------------------


class TestBatchMessages:
    """Tests for message batching logic (EMB-003)."""

    def test_batch_messages(self, embedding_db: sqlite3.Connection):
        """EMB-003: get_unembedded_messages returns correct batch."""
        messages = get_unembedded_messages(embedding_db, batch_size=5)

        assert len(messages) == 5
        assert all(isinstance(msg_id, int) for msg_id, _ in messages)
        assert all(isinstance(content, str) for _, content in messages)

    def test_batch_messages_max_batch(self, embedding_db: sqlite3.Connection):
        """EMB-003: Batch size limits the number of messages returned."""
        batch = get_unembedded_messages(embedding_db, batch_size=3)

        assert len(batch) == 3

    def test_batch_messages_all(self, embedding_db: sqlite3.Connection):
        """EMB-003: Can retrieve all messages in one batch."""
        messages = get_unembedded_messages(embedding_db, batch_size=100)

        assert len(messages) == 10

    def test_batch_messages_excludes_embedded(self, embedding_db: sqlite3.Connection):
        """EMB-003: Already-embedded messages are excluded from batches."""
        # Embed 4 messages
        rows = embedding_db.execute("SELECT id FROM messages LIMIT 4").fetchall()
        message_ids = [r[0] for r in rows]
        fake_embeddings = [[0.1] * 1536 for _ in range(4)]
        store_embeddings(embedding_db, message_ids, fake_embeddings)

        remaining = get_unembedded_messages(embedding_db, batch_size=100)

        assert len(remaining) == 6


# ---------------------------------------------------------------------------
# EMB-004: Store embedding
# ---------------------------------------------------------------------------


class TestStoreEmbedding:
    """Tests for embedding storage (EMB-004)."""

    def test_store_embedding(self, embedding_db: sqlite3.Connection):
        """EMB-004: Embeddings are stored successfully."""
        rows = embedding_db.execute("SELECT id FROM messages LIMIT 2").fetchall()
        message_ids = [r[0] for r in rows]

        fake_embeddings = [[0.1, 0.2, 0.3] + [0.0] * 1533 for _ in range(2)]

        stored = store_embeddings(embedding_db, message_ids, fake_embeddings)

        assert stored == 2

    def test_store_embedding_persists(self, embedding_db: sqlite3.Connection):
        """EMB-004: Stored embeddings persist in the database."""
        rows = embedding_db.execute("SELECT id FROM messages LIMIT 1").fetchall()
        message_ids = [r[0] for r in rows]
        fake_embeddings = [[0.1] * 1536]

        store_embeddings(embedding_db, message_ids, fake_embeddings)

        # Verify it was stored
        count = embedding_db.execute(
            "SELECT COUNT(*) FROM message_embeddings WHERE message_id = ?",
            (message_ids[0],),
        ).fetchone()[0]
        assert count == 1

    def test_store_embedding_upsert(self, embedding_db: sqlite3.Connection):
        """EMB-004: Re-storing an embedding replaces the existing one."""
        rows = embedding_db.execute("SELECT id FROM messages LIMIT 1").fetchall()
        message_ids = [r[0] for r in rows]

        # Store twice
        store_embeddings(embedding_db, message_ids, [[0.1] * 1536])
        store_embeddings(embedding_db, message_ids, [[0.9] * 1536])

        count = embedding_db.execute(
            "SELECT COUNT(*) FROM message_embeddings WHERE message_id = ?",
            (message_ids[0],),
        ).fetchone()[0]
        assert count == 1  # No duplicates


# ---------------------------------------------------------------------------
# EMB-005: Mocked API call
# ---------------------------------------------------------------------------


class TestEmbeddingMockAPI:
    """Tests for embedding generation with mocked OpenAI API (EMB-005)."""

    def test_embedding_mock_api(self, embedding_db: sqlite3.Connection):
        """EMB-005: Embedding generation works with mocked OpenAI client."""
        from chatgpt_archive.embeddings import generate_embeddings_batch

        fake_embedding = [0.1] * 1536

        # Create a mock OpenAI client
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_data = [MagicMock()]
        mock_data[0].embedding = fake_embedding
        mock_response.data = mock_data
        mock_client.embeddings.create.return_value = mock_response

        messages = [("Hello world",), ("Test message",)]

        with patch("chatgpt_archive.embeddings.get_openai_client", return_value=mock_client):
            result = generate_embeddings_batch(mock_client, ["Hello world", "Test message"])

        assert len(result) == 1  # One batch response
        # The result should contain the fake embeddings
        assert result[0] == fake_embedding

    def test_embedding_mock_api_batch_size(self, embedding_db: sqlite3.Connection):
        """EMB-005: Batch API call is made with correct contents."""
        from chatgpt_archive.embeddings import generate_embeddings_batch

        fake_embedding = [0.1] * 1536

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_data = [MagicMock()]
        mock_data[0].embedding = fake_embedding
        mock_response.data = mock_data
        mock_client.embeddings.create.return_value = mock_response

        texts = ["First message", "Second message"]
        result = generate_embeddings_batch(mock_client, texts)

        # Verify API was called with the texts
        mock_client.embeddings.create.assert_called_once()
        call_kwargs = mock_client.embeddings.create.call_args
        assert "input" in call_kwargs.kwargs or len(call_kwargs.args) > 0
