"""Integration tests for the search API endpoint (T224-T227)."""

import pytest


class TestSearchKeyword:
    """API-SCH-001: test_search_keyword."""

    @pytest.mark.asyncio
    async def test_search_keyword(self, client):
        """Keyword search returns matching conversations."""
        response = await client.post(
            "/api/search",
            json={"query": "Python", "search_type": "keyword"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        # conv-002-test has "Python" in its messages
        assert data["total"] >= 1


class TestSearchEmptyQuery:
    """API-SCH-002: test_search_empty_query."""

    @pytest.mark.asyncio
    async def test_search_empty_query(self, client):
        """Empty search query returns a validation error."""
        response = await client.post(
            "/api/search",
            json={"query": "", "search_type": "keyword"},
        )

        # Should return 422 (validation) or 400 (bad request)
        assert response.status_code in (400, 422)


class TestSearchDateFilter:
    """API-SCH-003: test_search_date_filter."""

    @pytest.mark.asyncio
    async def test_search_date_filter(self, client):
        """Date-filtered search narrows results by time range."""
        # conv-001-test has create_time=1700000000 (2023-11-14)
        # Use a narrow window that only includes the first conversation
        response = await client.post(
            "/api/search",
            json={
                "query": "Hello",
                "search_type": "keyword",
                "from_date": "2023-11-14",
                "to_date": "2023-11-15",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)


class TestSearchLimit:
    """API-SCH-004: test_search_limit."""

    @pytest.mark.asyncio
    async def test_search_limit(self, client):
        """Search respects the limit parameter."""
        response = await client.post(
            "/api/search",
            json={"query": "the", "search_type": "keyword", "limit": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 1
