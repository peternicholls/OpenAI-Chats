"""Integration tests for the favorites API endpoints (T243-T246)."""

import pytest


class TestToggleFavoriteOn:
    """API-FAV-001: test_toggle_favorite_on."""

    @pytest.mark.asyncio
    async def test_toggle_favorite_on(self, client):
        """Toggling favorite on an unfavorited conversation returns is_favorite=True."""
        response = await client.post("/api/conversations/conv-001-test/favorite")

        assert response.status_code == 200
        data = response.json()
        assert "is_favorite" in data
        assert data["is_favorite"] is True


class TestToggleFavoriteOff:
    """API-FAV-002: test_toggle_favorite_off."""

    @pytest.mark.asyncio
    async def test_toggle_favorite_off(self, client):
        """Toggling favorite twice returns is_favorite=False the second time."""
        # First toggle — on
        await client.post("/api/conversations/conv-001-test/favorite")

        # Second toggle — off
        response = await client.post("/api/conversations/conv-001-test/favorite")

        assert response.status_code == 200
        data = response.json()
        assert data["is_favorite"] is False


class TestListFavorites:
    """API-FAV-003: test_list_favorites."""

    @pytest.mark.asyncio
    async def test_list_favorites(self, client):
        """After favoriting a conversation it appears in the favorites list."""
        await client.post("/api/conversations/conv-001-test/favorite")

        response = await client.get("/api/favorites")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert any(item["id"] == "conv-001-test" for item in data["items"])


class TestListFavoritesEmpty:
    """API-FAV-004: test_list_favorites_empty."""

    @pytest.mark.asyncio
    async def test_list_favorites_empty(self, client):
        """With no favorited conversations the favorites list is empty."""
        response = await client.get("/api/favorites")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
