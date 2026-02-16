"""Tests for the tags endpoints."""

import pytest


class TestListTags:
    """Tests for GET /api/tags endpoint."""

    @pytest.mark.asyncio
    async def test_list_tags_returns_200(self, client):
        """Test that listing tags returns 200."""
        response = await client.get("/api/tags")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_tags_returns_array(self, client):
        """Test that listing tags returns an array."""
        response = await client.get("/api/tags")

        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_list_tags_initially_empty(self, client):
        """Test that tags list is initially empty."""
        response = await client.get("/api/tags")

        data = response.json()
        # No tags added yet in test fixtures
        assert len(data) == 0


class TestAddTag:
    """Tests for POST /api/conversations/{id}/tags endpoint."""

    @pytest.mark.asyncio
    async def test_add_tag_to_conversation(self, client):
        """Test adding a tag to a conversation."""
        response = await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "test-tag"}
        )

        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_add_tag_appears_in_list(self, client):
        """Test that added tag appears in tags list."""
        # Add a tag
        await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "my-tag"}
        )

        # Check it appears
        response = await client.get("/api/tags")
        data = response.json()
        tag_names = [t.get("name") for t in data]
        assert "my-tag" in tag_names

    @pytest.mark.asyncio
    async def test_add_tag_to_nonexistent_conversation(self, client):
        """Test adding tag to non-existent conversation fails."""
        response = await client.post(
            "/api/conversations/nonexistent/tags", json={"tag_name": "test-tag"}
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_add_empty_tag_rejected(self, client):
        """Test that empty tag names are rejected."""
        response = await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": ""}
        )

        assert response.status_code == 422


class TestRemoveTag:
    """Tests for DELETE /api/conversations/{id}/tags/{tag_name} endpoint."""

    @pytest.mark.asyncio
    async def test_remove_tag_from_conversation(self, client):
        """Test removing a tag from a conversation."""
        # First add a tag
        await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "to-remove"}
        )

        # Then remove it
        response = await client.delete("/api/conversations/conv-001-test/tags/to-remove")

        assert response.status_code == 204


class TestConversationTags:
    """Tests for GET /api/conversations/{id}/tags endpoint."""

    @pytest.mark.asyncio
    async def test_get_conversation_tags(self, client):
        """Test getting tags for a specific conversation."""
        # Add a tag first
        await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "conv-tag"}
        )

        response = await client.get("/api/conversations/conv-001-test/tags")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "conv-tag" in data
