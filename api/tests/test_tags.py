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


# ---------------------------------------------------------------------------
# T036 — Tag rename API tests (PUT /api/tags/{tag_name})
# ---------------------------------------------------------------------------


class TestRenameTag:
    """Tests for PUT /api/tags/{tag_name} endpoint."""

    @pytest.mark.asyncio
    async def test_rename_tag_returns_200(self, client):
        """Rename a known tag — expect 200 with updated tag data."""
        await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "old-tag"}
        )
        response = await client.put(
            "/api/tags/old-tag", json={"new_name": "new-tag"}
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rename_tag_updates_name(self, client):
        """After rename, new name appears and old name is gone."""
        await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "rename-me"}
        )
        await client.put("/api/tags/rename-me", json={"new_name": "renamed"})

        tags_resp = await client.get("/api/tags")
        names = [t["name"] for t in tags_resp.json()]
        assert "renamed" in names
        assert "rename-me" not in names

    @pytest.mark.asyncio
    async def test_rename_tag_propagates_to_conversations(self, client):
        """Renamed tag must appear in conversations that had the old tag."""
        await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "propagate-old"}
        )
        await client.put("/api/tags/propagate-old", json={"new_name": "propagate-new"})

        conv_tags = await client.get("/api/conversations/conv-001-test/tags")
        assert "propagate-new" in conv_tags.json()
        assert "propagate-old" not in conv_tags.json()

    @pytest.mark.asyncio
    async def test_rename_nonexistent_tag_returns_404(self, client):
        """Renaming a tag that doesn't exist should return 404."""
        response = await client.put(
            "/api/tags/ghost-tag", json={"new_name": "phantom-tag"}
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_rename_tag_empty_new_name_rejected(self, client):
        """Empty new_name should be rejected with 422."""
        await client.post(
            "/api/conversations/conv-001-test/tags", json={"tag_name": "valid-tag"}
        )
        response = await client.put("/api/tags/valid-tag", json={"new_name": ""})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_rename_tag_missing_new_name_rejected(self, client):
        """Missing new_name field should be rejected with 422."""
        response = await client.put("/api/tags/some-tag", json={})
        assert response.status_code == 422

