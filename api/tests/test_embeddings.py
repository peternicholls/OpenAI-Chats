"""Tests for embeddings endpoints."""

import sqlite3
from unittest.mock import patch

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

        monkeypatch.setattr(
            "api.routers.embeddings.validate_openai_api_key", fake_validate
        )

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

        monkeypatch.setattr(
            "api.routers.embeddings.validate_openai_api_key", fake_validate
        )
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

        monkeypatch.setattr(
            "api.routers.embeddings.validate_openai_api_key", fake_validate
        )
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


# ---------------------------------------------------------------------------
# T032 — Embedding workflow unit tests
# ---------------------------------------------------------------------------


class TestEstimateCostUnit:
    """Unit tests for chatgpt_archive.embeddings.estimate_cost."""

    def _make_db(self, tmp_path):
        from chatgpt_archive.db import init_db
        from chatgpt_archive.embeddings import init_embeddings_schema

        db_path = tmp_path / "est.db"
        conn = init_db(db_path)
        init_embeddings_schema(conn)
        conn.row_factory = sqlite3.Row
        return conn

    def test_estimate_cost_returns_required_fields(self, tmp_path):
        from chatgpt_archive.embeddings import estimate_cost

        conn = self._make_db(tmp_path)
        result = estimate_cost(conn)
        conn.close()
        assert "messages_to_embed" in result
        assert "total_characters" in result
        assert "price_per_million_tokens" in result
        assert "estimated_cost_display" in result
        assert "estimated_cost_usd" in result
        assert "model" in result

    def test_estimate_cost_no_init_embeddings_schema_side_effect(self, tmp_path):
        """T026 guard: estimate_cost must NOT call init_embeddings_schema."""
        from chatgpt_archive.embeddings import estimate_cost

        conn = self._make_db(tmp_path)

        # Verify that estimate_cost works on a properly-initialised DB
        # without calling init_embeddings_schema as a side effect.
        with patch("chatgpt_archive.embeddings.init_embeddings_schema") as mock_init:
            estimate_cost(conn)
            mock_init.assert_not_called()
        conn.close()

    def test_estimate_cost_empty_db_returns_zero(self, tmp_path):
        from chatgpt_archive.embeddings import estimate_cost

        conn = self._make_db(tmp_path)
        result = estimate_cost(conn)
        conn.close()
        assert result["messages_to_embed"] == 0
        assert result["total_characters"] == 0
        assert result["estimated_cost_usd"] == 0.0

    def test_estimate_cost_uses_requested_model(self, tmp_path):
        from chatgpt_archive.embeddings import PRICING, estimate_cost

        conn = self._make_db(tmp_path)
        result = estimate_cost(conn, model="text-embedding-3-large")
        conn.close()
        assert result["model"] == "text-embedding-3-large"
        assert result["price_per_million_tokens"] == PRICING["text-embedding-3-large"]


class TestCancellationFlagUnit:
    """Unit tests for threading.Event-based cancellation (T025)."""

    def test_cancel_sets_event(self):
        import api.services.archive_service as svc

        # Reset state first
        svc._embedding_cancelled.clear()
        svc._embedding_progress["status"] = "processing"

        assert svc.cancel_embedding_generation() is True
        assert svc.is_embedding_cancelled() is True

        # Cleanup
        svc.clear_embedding_cancellation()
        svc._embedding_progress["status"] = "idle"

    def test_clear_cancellation_clears_event(self):
        import api.services.archive_service as svc

        svc._embedding_cancelled.set()
        svc.clear_embedding_cancellation()
        assert svc.is_embedding_cancelled() is False

    def test_cancel_returns_false_when_idle(self):
        import api.services.archive_service as svc

        svc._embedding_cancelled.clear()
        svc._embedding_progress["status"] = "idle"

        assert svc.cancel_embedding_generation() is False

    def test_reset_clears_cancellation_flag(self):
        import api.services.archive_service as svc

        svc._embedding_cancelled.set()
        svc.reset_embedding_progress()
        assert svc.is_embedding_cancelled() is False
