"""Integration tests for the tags API endpoints (T237-T242)."""

import pytest


class TestListTagsEmpty:
    """API-TAG-001: test_list_tags_empty."""

    @pytest.mark.asyncio
    async def test_list_tags_empty(self, initialized_db, monkeypatch):
        """Empty database returns an empty tags list."""
        monkeypatch.setenv("CHATGPT_ARCHIVE_DB", str(initialized_db))
        monkeypatch.setenv("DB_PATH", str(initialized_db))

        from api.main import app
        from httpx import ASGITransport, AsyncClient

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/api/tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestListTagsWithCounts:
    """API-TAG-002: test_list_tags_with_counts."""

    @pytest.mark.asyncio
    async def test_list_tags_with_counts(self, client):
        """After adding tags, list returns tags with usage counts."""
        # Add a tag first
        await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "integration-test"},
        )

        response = await client.get("/api/tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        tag_names = [t["name"] for t in data]
        assert "integration-test" in tag_names
        tag = next(t for t in data if t["name"] == "integration-test")
        assert tag["count"] >= 1


class TestAddTag:
    """API-TAG-003: test_add_tag."""

    @pytest.mark.asyncio
    async def test_add_tag(self, client):
        """Adding a tag to a conversation succeeds with 204."""
        response = await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "new-tag"},
        )

        assert response.status_code == 204

        # Verify tag appears on conversation
        tags_resp = await client.get("/api/conversations/conv-001-test/tags")
        assert tags_resp.status_code == 200
        assert "new-tag" in tags_resp.json()


class TestAddTagDuplicate:
    """API-TAG-004: test_add_tag_duplicate."""

    @pytest.mark.asyncio
    async def test_add_tag_duplicate(self, client):
        """Adding a duplicate tag is idempotent (204 or 409)."""
        await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "duplicate-tag"},
        )

        response = await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "duplicate-tag"},
        )

        # Either idempotent success or conflict — both acceptable
        assert response.status_code in (204, 409)


class TestRemoveTag:
    """API-TAG-005: test_remove_tag."""

    @pytest.mark.asyncio
    async def test_remove_tag(self, client):
        """Removing a tag from a conversation succeeds with 204."""
        # Add tag first
        await client.post(
            "/api/conversations/conv-001-test/tags",
            json={"tag_name": "remove-me"},
        )

        response = await client.delete(
            "/api/conversations/conv-001-test/tags/remove-me"
        )

        assert response.status_code == 204

        # Verify tag is gone
        tags_resp = await client.get("/api/conversations/conv-001-test/tags")
        assert "remove-me" not in tags_resp.json()


class TestRemoveTagNotFound:
    """API-TAG-006: test_remove_tag_not_found."""

    @pytest.mark.asyncio
    async def test_remove_tag_not_found(self, client):
        """Removing a non-existent tag returns 404."""
        response = await client.delete(
            "/api/conversations/conv-001-test/tags/nonexistent-tag"
        )

        assert response.status_code == 404
