"""Tests for embeddings endpoints."""

import pytest


class TestEmbeddingStats:
    """Tests for GET /api/embeddings/stats endpoint."""

    @pytest.mark.asyncio
    async def test_stats_without_embedding_table_returns_zero(self, client):
        """Stats should work even before embeddings are generated."""
        response = await client.get("/api/embeddings/stats")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert data["withEmbeddings"] == 0


class TestValidateEmbeddingsKey:
    """Tests for POST /api/embeddings/validate-key endpoint."""

    @pytest.mark.asyncio
    async def test_validate_key_uses_request_body_key(self, client, monkeypatch):
        """Validation should use provided key when sent in request body."""
        seen: list[str] = []

        async def fake_validate(api_key: str):
            seen.append(api_key)
            return True, ""

        monkeypatch.setattr("api.routers.embeddings.validate_openai_api_key", fake_validate)

        response = await client.post(
            "/api/embeddings/validate-key", json={"api_key": "sk-provided"}
        )

        assert response.status_code == 200
        assert response.json()["valid"] is True
        assert seen == ["sk-provided"]

    @pytest.mark.asyncio
    async def test_validate_key_falls_back_to_stored_key(self, client, monkeypatch):
        """Validation should use stored key when request body has no key."""
        seen: list[str] = []

        async def fake_validate(api_key: str):
            seen.append(api_key)
            return True, ""

        monkeypatch.setattr("api.routers.embeddings.validate_openai_api_key", fake_validate)
        monkeypatch.setattr(
            "api.routers.embeddings.settings_service.get_setting", lambda _: "sk-stored"
        )

        response = await client.post("/api/embeddings/validate-key", json={})

        assert response.status_code == 200
        assert response.json()["valid"] is True
        assert seen == ["sk-stored"]


class TestGenerateEmbeddings:
    """Tests for POST /api/embeddings/generate endpoint."""

    @pytest.mark.asyncio
    async def test_generate_rejects_when_cost_exceeds_limit(self, client, monkeypatch):
        """Uses estimated_cost_usd to enforce max_cost before starting."""

        async def fake_validate(_api_key: str):
            return True, ""

        monkeypatch.setattr("api.routers.embeddings.validate_openai_api_key", fake_validate)
        monkeypatch.setattr(
            "api.routers.embeddings.settings_service.get_setting", lambda _: "sk-stored"
        )
        monkeypatch.setattr(
            "chatgpt_archive.embeddings.estimate_cost",
            lambda _conn, model=None: {"estimated_cost_usd": 12.5, "model": model},
        )

        response = await client.post(
            "/api/embeddings/generate",
            json={
                "model": "text-embedding-3-small",
                "batch_size": 100,
                "max_cost": 1.0,
                "estimate_only": False,
            },
        )

        assert response.status_code == 400
        assert "exceeds" in response.json()["detail"].lower()
