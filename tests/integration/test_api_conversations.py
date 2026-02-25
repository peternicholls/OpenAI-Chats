"""Integration tests for the conversations API endpoints (T216-T223)."""

import pytest


class TestListConversationsEmpty:
    """API-CONV-001: test_list_conversations_empty."""

    @pytest.mark.asyncio
    async def test_list_conversations_empty(self, initialized_db, monkeypatch, tmp_path):
        """Empty database returns empty items list with total=0."""
        monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(initialized_db))
        monkeypatch.setenv("DB_PATH", str(initialized_db))

        from api.main import app
        from httpx import ASGITransport, AsyncClient

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/conversations")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []


class TestListConversationsPaginated:
    """API-CONV-002: test_list_conversations_paginated."""

    @pytest.mark.asyncio
    async def test_list_conversations_paginated(self, client):
        """Pagination returns correct slice of conversations."""
        response = await client.get("/api/conversations?limit=2&offset=0")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["limit"] == 2
        assert data["offset"] == 0
        assert data["total"] == 3


class TestListConversationsSortedDate:
    """API-CONV-003: test_list_conversations_sorted_date."""

    @pytest.mark.asyncio
    async def test_list_conversations_sorted_date_desc(self, client):
        """Conversations are returned newest-first by default."""
        response = await client.get("/api/conversations?sort_by=date&order=desc")

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        times = [item["create_time"] for item in items]
        assert times == sorted(times, reverse=True)

    @pytest.mark.asyncio
    async def test_list_conversations_sorted_date_asc(self, client):
        """Conversations are returned oldest-first when order=asc."""
        response = await client.get("/api/conversations?sort_by=date&order=asc")

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        times = [item["create_time"] for item in items]
        assert times == sorted(times)


class TestListConversationsSortedTitle:
    """API-CONV-004: test_list_conversations_sorted_title."""

    @pytest.mark.asyncio
    async def test_list_conversations_sorted_title(self, client):
        """Conversations can be sorted by title."""
        response = await client.get("/api/conversations?sort_by=title&order=asc")

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        titles = [item["title"] for item in items]
        assert titles == sorted(titles, key=lambda t: (t or "").lower())


class TestGetConversationExists:
    """API-CONV-005: test_get_conversation_exists."""

    @pytest.mark.asyncio
    async def test_get_conversation_exists(self, client):
        """Fetching an existing conversation returns its full detail."""
        response = await client.get("/api/conversations/conv-001-test")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "conv-001-test"
        assert data["title"] == "Test Conversation 1"
        assert "messages" in data


class TestGetConversationNotFound:
    """API-CONV-006: test_get_conversation_not_found."""

    @pytest.mark.asyncio
    async def test_get_conversation_not_found(self, client):
        """Fetching a non-existent conversation returns 404."""
        response = await client.get("/api/conversations/does-not-exist")

        assert response.status_code == 404


class TestDeleteConversation:
    """API-CONV-007: test_delete_conversation."""

    @pytest.mark.asyncio
    async def test_delete_conversation(self, client):
        """Deleting an existing conversation returns 204 and removes it."""
        delete_resp = await client.delete("/api/conversations/conv-001-test")
        assert delete_resp.status_code == 204

        get_resp = await client.get("/api/conversations/conv-001-test")
        assert get_resp.status_code == 404


class TestDeleteConversationNotFound:
    """API-CONV-008: test_delete_conversation_not_found."""

    @pytest.mark.asyncio
    async def test_delete_conversation_not_found(self, client):
        """Deleting a non-existent conversation returns 404."""
        response = await client.delete("/api/conversations/ghost-id")

        assert response.status_code == 404
