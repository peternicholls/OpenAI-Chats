"""Tests for the conversations endpoints."""

import pytest


class TestListConversations:
    """Tests for GET /api/conversations endpoint."""

    @pytest.mark.asyncio
    async def test_list_conversations_returns_200(self, client):
        """Test that listing conversations returns 200."""
        response = await client.get("/api/conversations")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_conversations_returns_items(self, client):
        """Test that listing returns the expected structure."""
        response = await client.get("/api/conversations")

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data

    @pytest.mark.asyncio
    async def test_list_conversations_contains_sample_data(self, client):
        """Test that sample conversations are returned."""
        response = await client.get("/api/conversations")

        data = response.json()
        assert data["total"] == 3  # We have 3 sample conversations
        assert len(data["items"]) == 3
        assert {item["id"] for item in data["items"]} == {
            "conv-001-test",
            "conv-002-test",
            "conv-003-test",
        }

    @pytest.mark.asyncio
    async def test_list_conversations_pagination_limit(self, client):
        """Test pagination with limit parameter."""
        response = await client.get("/api/conversations?limit=2")

        data = response.json()
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        # Default ordering is date desc: conv-003 then conv-002.
        assert [item["id"] for item in data["items"]] == [
            "conv-003-test",
            "conv-002-test",
        ]

    @pytest.mark.asyncio
    async def test_list_conversations_pagination_offset(self, client):
        """Test pagination with offset parameter."""
        response = await client.get("/api/conversations?offset=2")

        data = response.json()
        assert len(data["items"]) == 1  # 3 total - 2 offset = 1 remaining
        assert data["offset"] == 2
        assert data["items"][0]["id"] == "conv-001-test"

    @pytest.mark.asyncio
    async def test_list_conversations_sorted_by_date(self, client):
        """Test sorting by date descending (default)."""
        response = await client.get("/api/conversations?sort_by=date&order=desc")

        data = response.json()
        items = data["items"]
        # Most recent first (conv-003 has highest create_time)
        assert items[0]["id"] == "conv-003-test"

    @pytest.mark.asyncio
    async def test_list_conversations_includes_required_fields(self, client):
        """Test that conversation items include all required fields."""
        response = await client.get("/api/conversations")

        data = response.json()
        item = data["items"][0]
        assert "id" in item
        assert "title" in item
        assert "create_time" in item
        assert "message_count" in item
        assert "tags" in item
        assert "is_favorite" in item


class TestGetConversation:
    """Tests for GET /api/conversations/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_get_conversation_by_id(self, client):
        """Test getting a single conversation by ID."""
        response = await client.get("/api/conversations/conv-001-test")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "conv-001-test"
        assert data["title"] == "Test Conversation 1"

    @pytest.mark.asyncio
    async def test_get_conversation_includes_messages(self, client):
        """Test that conversation detail includes messages."""
        response = await client.get("/api/conversations/conv-001-test")

        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 2

    @pytest.mark.asyncio
    async def test_get_conversation_messages_have_required_fields(self, client):
        """Test that messages have required fields."""
        response = await client.get("/api/conversations/conv-001-test")

        data = response.json()
        first, second = data["messages"]
        assert first["id"] == "msg-001"
        assert first["role"] == "user"
        assert first["content"] == "Hello, how are you?"
        assert second["id"] == "msg-002"
        assert second["role"] == "assistant"
        assert "thank you" in second["content"]
        assert first["attachments"] == []
        assert second["attachments"] == []
        assert first["segments"] == [{
            "kind": "markdown",
            "text": "Hello, how are you?",
            "attachment_index": None,
            "fallback_label": None,
        }]
        assert second["segments"] == [{
            "kind": "markdown",
            "text": "I'm doing well, thank you for asking!",
            "attachment_index": None,
            "fallback_label": None,
        }]

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, client):
        """Test getting a non-existent conversation returns 404."""
        response = await client.get("/api/conversations/non-existent-id")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_conversation_404_has_error_detail(self, client):
        """Test that 404 response includes error detail."""
        response = await client.get("/api/conversations/non-existent-id")

        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_get_conversation_with_media_keeps_text_and_attachment_order(
        self, media_client
    ):
        response = await media_client.get(
            "/api/conversations/68e06336-bce4-8330-b350-f7a33ffac85e"
        )

        assert response.status_code == 200
        message = response.json()["messages"][0]
        assert message["content"].startswith("Lead text")
        assert "[[ATTACHMENT:0]]" in message["content"]
        assert len(message["attachments"]) == 3
        assert [segment["kind"] for segment in message["segments"]] == [
            "markdown",
            "attachment",
            "markdown",
            "attachment",
            "attachment",
        ]

    @pytest.mark.asyncio
    async def test_get_conversation_includes_segments_for_attachment_only_messages(
        self, media_client
    ):
        response = await media_client.get(
            "/api/conversations/68e06336-bce4-8330-b350-f7a33ffac85e"
        )

        assert response.status_code == 200
        message = response.json()["messages"][1]
        assert message["content"].startswith("[[ATTACHMENT:0]]")
        assert message["segments"][0] == {
            "kind": "attachment",
            "text": None,
            "attachment_index": 0,
            "fallback_label": None,
        }

    @pytest.mark.asyncio
    async def test_get_conversation_replaces_recognized_asset_payloads_with_segments_only(
        self, media_client
    ):
        response = await media_client.get(
            "/api/conversations/68e06336-bce4-8330-b350-f7a33ffac85e"
        )

        assert response.status_code == 200
        message = response.json()["messages"][0]
        assert "asset_pointer" not in message["content"]
        assert [segment["kind"] for segment in message["segments"]] == [
            "markdown",
            "attachment",
            "markdown",
            "attachment",
            "attachment",
        ]

    @pytest.mark.asyncio
    async def test_get_conversation_text_only_messages_keep_empty_attachments(self, client):
        response = await client.get("/api/conversations/conv-002-test")

        assert response.status_code == 200
        for message in response.json()["messages"]:
            assert message["attachments"] == []

    @pytest.mark.asyncio
    async def test_get_conversation_returns_markdown_segments_for_formatted_messages(
        self, formatted_client
    ):
        response = await formatted_client.get("/api/conversations/conv-formatted-001")

        assert response.status_code == 200
        message = response.json()["messages"][0]
        assert message["segments"] == [
            {
                "kind": "markdown",
                "text": (
                    "# Release Notes\n\n"
                    "- Added **formatted** transcript rendering\n"
                    "- Supports [links](https://example.com) and `inline code`\n\n"
                    "> Blockquotes remain readable\n\n"
                    "```python\nprint('hello')\n```"
                ),
                "attachment_index": None,
                "fallback_label": None,
            }
        ]

    @pytest.mark.asyncio
    async def test_get_conversation_resolves_inline_citations_from_message_metadata(
        self, formatted_client
    ):
        response = await formatted_client.get("/api/conversations/conv-formatted-001")

        assert response.status_code == 200
        message = response.json()["messages"][1]
        assert message["content"] == "Research summary ([Example Source](https://example.com/source))"
        assert message["segments"] == [
            {
                "kind": "markdown",
                "text": "Research summary ([Example Source](https://example.com/source))",
                "attachment_index": None,
                "fallback_label": None,
            }
        ]

    @pytest.mark.asyncio
    async def test_get_conversation_keeps_missing_attachment_as_attachment_segment(
        self, media_client
    ):
        response = await media_client.get(
            "/api/conversations/68e06336-bce4-8330-b350-f7a33ffac85e"
        )

        assert response.status_code == 200
        message = response.json()["messages"][1]
        assert message["attachments"][0]["found"] is False
        assert message["segments"] == [
            {
                "kind": "attachment",
                "text": None,
                "attachment_index": 0,
                "fallback_label": None,
            }
        ]


class TestListConversationsEmpty:
    """Tests for empty database scenarios."""

    @pytest.mark.asyncio
    async def test_list_empty_database(self, monkeypatch, tmp_path):
        """Test listing conversations when database is empty."""
        from httpx import ASGITransport, AsyncClient

        from chatgpt_archive import db

        empty_db = tmp_path / "empty.db"
        conn = db.init_db(empty_db)
        conn.close()

        monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(empty_db))
        monkeypatch.setenv("DB_PATH", str(empty_db))

        from api.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/conversations")

        # Should still return 200 with empty items
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestThinkingSegmentScoping:
    """T031: Processing clusters must only produce ThinkingSegments on assistant turns."""

    def _make_db(self, tmp_path):
        """Return an open connection to a fresh in-memory-style DB seeded with a
        conversation that has a processing (thoughts) turn followed by a user message."""
        from chatgpt_archive import db as cga_db

        db_path = tmp_path / "thinking.db"
        conn = cga_db.init_db(db_path)

        conn.execute(
            """
            INSERT INTO conversations (openai_id, title, create_time, update_time)
            VALUES ('think-test-conv', 'Thinking Test', 1700000000, 1700000000)
            """
        )
        conv_id = conn.execute(
            "SELECT id FROM conversations WHERE openai_id = 'think-test-conv'"
        ).fetchone()["id"]

        # A processing (thoughts) turn — author_role assistant, content_type thoughts
        conn.execute(
            """
            INSERT INTO messages
                (conversation_id, openai_id, author_role, content_type, content, create_time)
            VALUES (?, 'msg-thoughts', 'assistant', 'thoughts', 'thinking...', 1700000001)
            """,
            (conv_id,),
        )
        # A user message that immediately follows the processing turn
        conn.execute(
            """
            INSERT INTO messages
                (conversation_id, openai_id, author_role, content_type, content, create_time)
            VALUES (?, 'msg-user', 'user', 'text', 'Here is my image', 1700000002)
            """,
            (conv_id,),
        )
        # A normal assistant reply
        conn.execute(
            """
            INSERT INTO messages
                (conversation_id, openai_id, author_role, content_type, content, create_time)
            VALUES (?, 'msg-assistant', 'assistant', 'text', 'Nice image!', 1700000003)
            """,
            (conv_id,),
        )

        conn.commit()
        conn.close()
        return db_path

    def test_thinking_segment_not_attached_to_user_message(self, tmp_path, monkeypatch):
        """A processing cluster followed by a user turn must not produce a ThinkingSegment
        on that user message (T031 / H4 from visual review)."""
        db_path = self._make_db(tmp_path)

        monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(db_path))
        monkeypatch.setenv("DB_PATH", str(db_path))

        from api.services import archive_service

        detail = archive_service.get_conversation("think-test-conv")

        user_messages = [m for m in detail["messages"] if m["role"] == "user"]
        assert user_messages, "expected at least one user message"
        user_msg = user_messages[0]

        thinking_segs = [s for s in (user_msg.get("segments") or []) if s.kind == "thinking"]
        assert thinking_segs == [], (
            "ThinkingSegment must not appear on a user-role message"
        )

        assert detail["message_count"] == 3
        assert detail["visible_message_count"] == 2
