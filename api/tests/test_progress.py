"""Tests for SSE stream termination on terminal status values.

T035: Verifies that import and embedding progress streams break on
"complete", "error", "idle", and "cancelled" statuses (T009 fix).
"""

import json
from unittest.mock import AsyncMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helper: collect all SSE events from the generator
# ---------------------------------------------------------------------------


async def _drain(generator) -> list[dict]:
    """Collect all SSE data events from an async generator."""
    events = []
    async for chunk in generator:
        if chunk.startswith("data: "):
            payload = chunk[len("data: ") :].strip()
            if payload:
                events.append(json.loads(payload))
    return events


def _idle_request():
    """Mock request that is never disconnected."""
    req = AsyncMock()
    req.is_disconnected = AsyncMock(return_value=False)
    return req


# ---------------------------------------------------------------------------
# Import stream tests
# ---------------------------------------------------------------------------


class TestImportProgressStream:
    """SSE termination behaviour for /api/import/progress/stream."""

    @pytest.mark.asyncio
    async def test_stream_terminates_on_complete(self):
        progress = {
            "status": "complete",
            "current": 10,
            "total": 10,
            "percent": 100.0,
            "message": "Done",
        }
        with patch(
            "api.routers.progress.archive_service.get_import_progress",
            return_value=progress,
        ):
            from api.routers.progress import stream_import_progress

            response = await stream_import_progress(_idle_request())
            events = await _drain(response.body_iterator)
        assert any(e["status"] == "complete" for e in events)
        # Stream must stop — exactly one event in this case
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_stream_terminates_on_error(self):
        progress = {
            "status": "error",
            "current": 0,
            "total": 0,
            "percent": 0.0,
            "message": "Oops",
        }
        with patch(
            "api.routers.progress.archive_service.get_import_progress",
            return_value=progress,
        ):
            from api.routers.progress import stream_import_progress

            response = await stream_import_progress(_idle_request())
            events = await _drain(response.body_iterator)
        assert any(e["status"] == "error" for e in events)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_stream_terminates_on_cancelled(self):
        """T009: 'cancelled' must cause the stream to break."""
        progress = {
            "status": "cancelled",
            "current": 3,
            "total": 10,
            "percent": 30.0,
            "message": "Cancelled",
        }
        with patch(
            "api.routers.progress.archive_service.get_import_progress",
            return_value=progress,
        ):
            from api.routers.progress import stream_import_progress

            response = await stream_import_progress(_idle_request())
            events = await _drain(response.body_iterator)
        assert any(e["status"] == "cancelled" for e in events)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_stream_terminates_on_idle(self):
        progress = {
            "status": "idle",
            "current": 0,
            "total": 0,
            "percent": 0.0,
            "message": None,
        }
        with patch(
            "api.routers.progress.archive_service.get_import_progress",
            return_value=progress,
        ):
            from api.routers.progress import stream_import_progress

            response = await stream_import_progress(_idle_request())
            events = await _drain(response.body_iterator)
        assert any(e["status"] == "idle" for e in events)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_stream_continues_while_processing(self):
        """Stream emits events while status stays 'processing', stops on complete."""
        call_count = 0
        responses = [
            {
                "status": "processing",
                "current": 1,
                "total": 10,
                "percent": 10.0,
                "message": "...",
            },
            {
                "status": "processing",
                "current": 5,
                "total": 10,
                "percent": 50.0,
                "message": "...",
            },
            {
                "status": "complete",
                "current": 10,
                "total": 10,
                "percent": 100.0,
                "message": "Done",
            },
        ]

        def _next_progress():
            nonlocal call_count
            idx = min(call_count, len(responses) - 1)
            call_count += 1
            return responses[idx]

        with (
            patch(
                "api.routers.progress.archive_service.get_import_progress",
                side_effect=_next_progress,
            ),
            patch("asyncio.sleep", new_callable=AsyncMock),
        ):
            from api.routers.progress import stream_import_progress

            response = await stream_import_progress(_idle_request())
            events = await _drain(response.body_iterator)

        statuses = [e["status"] for e in events]
        assert "processing" in statuses
        assert statuses[-1] == "complete"


# ---------------------------------------------------------------------------
# Embedding stream tests
# ---------------------------------------------------------------------------


class TestEmbeddingProgressStream:
    """SSE termination behaviour for /api/embeddings/progress/stream."""

    @pytest.mark.asyncio
    async def test_stream_terminates_on_cancelled(self):
        """T009: 'cancelled' must cause the embedding stream to break."""
        progress = {
            "status": "cancelled",
            "current": 2,
            "total": 5,
            "percent": 40.0,
            "message": "Cancelled",
        }
        with patch(
            "api.routers.progress.archive_service.get_embedding_progress",
            return_value=progress,
        ):
            from api.routers.progress import stream_embedding_progress

            response = await stream_embedding_progress(_idle_request())
            events = await _drain(response.body_iterator)
        assert any(e["status"] == "cancelled" for e in events)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_stream_terminates_on_complete(self):
        progress = {
            "status": "complete",
            "current": 5,
            "total": 5,
            "percent": 100.0,
            "message": "Done",
        }
        with patch(
            "api.routers.progress.archive_service.get_embedding_progress",
            return_value=progress,
        ):
            from api.routers.progress import stream_embedding_progress

            response = await stream_embedding_progress(_idle_request())
            events = await _drain(response.body_iterator)
        assert any(e["status"] == "complete" for e in events)
