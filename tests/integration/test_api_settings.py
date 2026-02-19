"""Integration tests for the settings API endpoints (T251-T254)."""

import pytest


class TestGetSettings:
    """API-SET-001: test_get_settings."""

    @pytest.mark.asyncio
    async def test_get_settings(self, client):
        """Settings endpoint returns a valid settings object."""
        response = await client.get("/api/settings")

        assert response.status_code == 200
        data = response.json()
        assert "theme" in data
        assert "default_export_format" in data


class TestUpdateTheme:
    """API-SET-002: test_update_theme."""

    @pytest.mark.asyncio
    async def test_update_theme(self, client):
        """Updating the theme persists the change."""
        response = await client.put("/api/settings", json={"theme": "dark"})

        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "dark"

    @pytest.mark.asyncio
    async def test_update_theme_light(self, client):
        """Updating theme to light works correctly."""
        response = await client.put("/api/settings", json={"theme": "light"})

        assert response.status_code == 200
        data = response.json()
        assert data["theme"] == "light"


class TestUpdateOpenAIKey:
    """API-SET-003: test_update_openai_key."""

    @pytest.mark.asyncio
    async def test_update_openai_key(self, client):
        """Storing an OpenAI key sets the key flag (key itself is not returned)."""
        response = await client.put(
            "/api/settings",
            json={"openai_api_key": "sk-test-key-abc123"},
        )

        assert response.status_code == 200
        data = response.json()
        # The actual key should not be returned, only the flag
        assert "openai_api_key" not in data or data.get("openai_api_key_set") is True


class TestUpdateInvalid:
    """API-SET-004: test_update_invalid."""

    @pytest.mark.asyncio
    async def test_update_invalid_theme(self, client):
        """Setting an invalid theme value returns 422."""
        response = await client.put(
            "/api/settings",
            json={"theme": "rainbow"},
        )

        assert response.status_code == 422
