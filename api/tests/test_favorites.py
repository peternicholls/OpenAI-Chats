"""Tests for the favorites endpoints."""

import pytest


class TestToggleFavorite:
    """Tests for POST /api/favorites/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_toggle_favorite_returns_200(self, client):
        """Test toggling favorite status returns 200."""
        response = await client.post("/api/conversations/conv-001-test/favorite")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_toggle_favorite_returns_new_status(self, client):
        """Test that toggle returns the new favorite status."""
        response = await client.post("/api/conversations/conv-001-test/favorite")

        data = response.json()
        assert "is_favorite" in data
        assert isinstance(data["is_favorite"], bool)

    @pytest.mark.asyncio
    async def test_toggle_favorite_toggles_status(self, client):
        """Test that calling toggle twice reverts status."""
        # First toggle
        response1 = await client.post("/api/conversations/conv-002-test/favorite")
        status1 = response1.json()["is_favorite"]

        # Second toggle
        response2 = await client.post("/api/conversations/conv-002-test/favorite")
        status2 = response2.json()["is_favorite"]

        assert status1 != status2

    @pytest.mark.asyncio
    async def test_toggle_favorite_nonexistent_returns_404(self, client):
        """Test toggling favorite on non-existent conversation returns 404."""
        response = await client.post("/api/conversations/nonexistent-id/favorite")

        assert response.status_code == 404


class TestListFavorites:
    """Tests for GET /api/favorites endpoint."""

    @pytest.mark.asyncio
    async def test_list_favorites_returns_200(self, client):
        """Test listing favorites returns 200."""
        response = await client.get("/api/favorites")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_favorites_returns_structure(self, client):
        """Test favorites list has expected structure."""
        response = await client.get("/api/favorites")

        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_favorites_initially_empty(self, client):
        """Test favorites list is initially empty."""
        response = await client.get("/api/favorites")

        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_favorited_conversation_appears_in_list(self, client):
        """Test that favoriting a conversation adds it to the list."""
        # Favorite a conversation
        await client.post("/api/conversations/conv-003-test/favorite")

        # Check it appears in list
        response = await client.get("/api/favorites")
        data = response.json()

        ids = [item["id"] for item in data["items"]]
        assert "conv-003-test" in ids

    @pytest.mark.asyncio
    async def test_unfavorited_removed_from_list(self, client):
        """Test that unfavoriting removes from list."""
        # Favorite then unfavorite
        await client.post("/api/conversations/conv-001-test/favorite")
        await client.post("/api/conversations/conv-001-test/favorite")

        response = await client.get("/api/favorites")
        data = response.json()

        ids = [item["id"] for item in data["items"]]
        assert "conv-001-test" not in ids
