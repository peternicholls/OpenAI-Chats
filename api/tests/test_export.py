"""Tests for the export endpoints."""

import pytest


class TestExport:
    """Tests for GET /api/export/{id} endpoint."""

    @pytest.mark.asyncio
    async def test_export_markdown_returns_200(self, client):
        """Test exporting as Markdown returns 200."""
        response = await client.get("/api/conversations/conv-001-test/export?format=md")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_export_markdown_content_type(self, client):
        """Test Markdown export has correct content type."""
        response = await client.get("/api/conversations/conv-001-test/export?format=md")

        assert "text/markdown" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_markdown_contains_content(self, client):
        """Test Markdown export contains conversation content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=md")

        content = response.text
        assert "Test Conversation 1" in content
        assert "Hello, how are you?" in content

    @pytest.mark.asyncio
    async def test_export_json_returns_200(self, client):
        """Test exporting as JSON returns 200."""
        response = await client.get("/api/conversations/conv-001-test/export?format=json")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_export_json_is_valid(self, client):
        """Test JSON export is valid JSON."""
        response = await client.get("/api/conversations/conv-001-test/export?format=json")

        data = response.json()
        assert data["id"] == "conv-001-test"
        assert len(data["messages"]) == 2

    @pytest.mark.asyncio
    async def test_export_json_content_type(self, client):
        """Test JSON export has correct content type."""
        response = await client.get("/api/conversations/conv-001-test/export?format=json")

        assert "application/json" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_export_yaml_returns_200(self, client):
        """Test exporting as YAML returns expected type and content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=yaml")

        assert response.status_code == 200
        assert "application/x-yaml" in response.headers.get("content-type", "")
        assert "id: conv-001-test" in response.text

    @pytest.mark.asyncio
    async def test_export_html_returns_200(self, client):
        """Test exporting as HTML returns expected type and content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=html")

        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "<html" in response.text.lower()

    @pytest.mark.asyncio
    async def test_export_csv_returns_200(self, client):
        """Test exporting as CSV returns expected type and content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=csv")

        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
        assert "message_id,role,content" in response.text

    @pytest.mark.asyncio
    async def test_export_invalid_format_returns_error(self, client):
        """Test invalid export format returns error."""
        response = await client.get("/api/conversations/conv-001-test/export?format=invalid")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_nonexistent_conversation_returns_404(self, client):
        """Test exporting non-existent conversation returns 404."""
        response = await client.get("/api/conversations/nonexistent-id/export?format=md")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_export_has_content_disposition(self, client):
        """Test export has Content-Disposition header for download."""
        response = await client.get("/api/conversations/conv-001-test/export?format=md")

        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
        assert response.headers["content-disposition"].endswith(".md\"")
