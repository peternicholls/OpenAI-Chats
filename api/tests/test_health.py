"""Tests for the health check endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    """Test that health endpoint returns 200 with status ok."""
    response = await client.get("/api/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_health_endpoint_returns_correct_content_type(client):
    """Test that health endpoint returns JSON content type."""
    response = await client.get("/api/health")

    assert response.headers["content-type"] == "application/json"
