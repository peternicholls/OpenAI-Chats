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
        """Test invalid export format returns 400 (enum validation)."""
        response = await client.get("/api/conversations/conv-001-test/export?format=invalid")

        # FastAPI returns 400 for invalid enum values (via Starlette)
        assert response.status_code == 400

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

    @pytest.mark.asyncio
    async def test_export_xml_returns_200(self, client):
        """Test exporting as XML returns expected type and content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=xml")

        assert response.status_code == 200
        assert "application/xml" in response.headers.get("content-type", "")
        assert "<?xml" in response.text
        assert "conv-001-test" in response.text

    @pytest.mark.asyncio
    async def test_export_xlsx_returns_200(self, client):
        """Test exporting as XLSX returns expected type and binary content."""
        response = await client.get("/api/conversations/conv-001-test/export?format=xlsx")

        assert response.status_code == 200
        content_type = response.headers.get("content-type", "")
        assert "spreadsheetml" in content_type or "xlsx" in content_type.lower()
        # XLSX files start with PK (ZIP signature)
        assert response.content[:2] == b"PK"


class TestBatchExport:
    """Tests for batch export functionality."""

    @pytest.mark.asyncio
    async def test_batch_export_multiple_conversations_md(self, client):
        """Test batch export of multiple conversations as Markdown."""
        response = await client.get(
            "/api/export/batch?ids=conv-001-test,conv-002-test&format=md"
        )

        assert response.status_code == 200
        assert "text/markdown" in response.headers.get("content-type", "")
        content = response.text
        assert "Test Conversation 1" in content
        assert "Test Conversation 2" in content

    @pytest.mark.asyncio
    async def test_batch_export_multiple_conversations_json(self, client):
        """Test batch export of multiple conversations as JSON."""
        response = await client.get(
            "/api/export/batch?ids=conv-001-test,conv-002-test&format=json"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        ids = [c["id"] for c in data]
        assert "conv-001-test" in ids
        assert "conv-002-test" in ids

    @pytest.mark.asyncio
    async def test_batch_export_all_formats(self, client):
        """T102: Validate all 7 export formats work correctly for batch export."""
        formats = [
            ("md", "text/markdown"),
            ("json", "application/json"),
            ("yaml", "application/x-yaml"),
            ("html", "text/html"),
            ("xml", "application/xml"),
            ("csv", "text/csv"),
            ("xlsx", "spreadsheetml"),
        ]

        for fmt, expected_content_type in formats:
            response = await client.get(
                f"/api/export/batch?ids=conv-001-test,conv-002-test&format={fmt}"
            )

            assert response.status_code == 200, f"Format {fmt} failed with status {response.status_code}"
            content_type = response.headers.get("content-type", "")
            assert expected_content_type in content_type, (
                f"Format {fmt} has wrong content-type: {content_type}"
            )
            assert "content-disposition" in response.headers
            assert "attachment" in response.headers["content-disposition"]

    @pytest.mark.asyncio
    async def test_batch_export_no_ids_returns_400(self, client):
        """Test batch export with no IDs returns 400."""
        response = await client.get("/api/export/batch?ids=&format=md")

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_batch_export_nonexistent_id_returns_404(self, client):
        """Test batch export with non-existent ID returns 404."""
        response = await client.get(
            "/api/export/batch?ids=nonexistent-id&format=md"
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_batch_export_partial_nonexistent_returns_404(self, client):
        """Test batch export with some non-existent IDs returns 404."""
        response = await client.get(
            "/api/export/batch?ids=conv-001-test,nonexistent-id&format=md"
        )

        assert response.status_code == 404
