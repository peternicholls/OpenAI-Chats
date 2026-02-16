"""Tests for the search endpoint."""

import pytest


class TestSearch:
    """Tests for POST /api/search endpoint."""

    @pytest.mark.asyncio
    async def test_search_basic_returns_200(self, client):
        """Test that search returns 200."""
        response = await client.post("/api/search", json={"query": "hello"})

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_returns_results_structure(self, client):
        """Test that search returns expected structure."""
        response = await client.post("/api/search", json={"query": "hello"})

        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_search_finds_matching_content(self, client):
        """Test that search finds conversations with matching content."""
        response = await client.post("/api/search", json={"query": "Python"})

        data = response.json()
        assert data["total"] > 0
        # Should find conversation about Python
        titles = [item["title"] for item in data["items"]]
        assert any("Python" in title or "Test Conversation 2" in title for title in titles)

    @pytest.mark.asyncio
    async def test_search_empty_results(self, client):
        """Test search with no matches returns empty results."""
        response = await client.post("/api/search", json={"query": "xyznonexistent123"})

        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    @pytest.mark.asyncio
    async def test_search_with_limit(self, client):
        """Test search respects limit parameter."""
        response = await client.post("/api/search", json={"query": "test", "limit": 1})

        data = response.json()
        assert len(data["items"]) <= 1

    @pytest.mark.asyncio
    async def test_search_result_has_required_fields(self, client):
        """Test that search results include required fields."""
        response = await client.post("/api/search", json={"query": "hello"})

        data = response.json()
        if data["items"]:
            item = data["items"][0]
            assert "conversation_id" in item
            assert "title" in item
            assert "preview" in item

    @pytest.mark.asyncio
    async def test_search_empty_query_handled(self, client):
        """Test that empty query is handled gracefully."""
        response = await client.post("/api/search", json={"query": ""})

        # Should return 400 or empty results, not error
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_search_missing_query_returns_422(self, client):
        """Test that missing query field returns validation error."""
        response = await client.post("/api/search", json={})

        assert response.status_code == 422  # Validation error


class TestSearchTypes:
    """Tests for different search types."""

    @pytest.mark.asyncio
    async def test_search_keyword_type(self, client):
        """Test keyword search type (default)."""
        response = await client.post(
            "/api/search", json={"query": "machine learning", "search_type": "keyword"}
        )

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_search_invalid_type_handled(self, client):
        """Test that invalid search type is handled."""
        response = await client.post(
            "/api/search", json={"query": "test", "search_type": "invalid_type"}
        )

        # Should either return 400/422 or fall back to keyword
        assert response.status_code in [200, 400, 422]
